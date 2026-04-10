import json
import os
from typing import List, Dict, Any
import google.generativeai as genai
from pdf_processor import PDFProcessor
from compliance_rules import get_rules  # ← NEW: mode-aware
from config import GEMINI_API_KEY, MODEL_NAME, RESULTS_FILE
from datetime import datetime


class ComplianceChecker:
    def __init__(self, mode: str = "rent"):  # ← NEW: mode parameter
        # Configure Gemini API
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(MODEL_NAME)
        
        # Initialize PDF processor
        self.pdf_processor = PDFProcessor()
        self.pdf_processor.load_vector_store()
        
        # Load compliance rules for SPECIFIC MODE
        self.rules = get_rules(mode)  # ← NEW: mode-aware
        self.mode = mode
        
    def check_rule_compliance(self, rule: Dict) -> Dict[str, Any]:
        """Check compliance for a specific rule (list-based now)"""
        rule_id = rule['rule_id']
        
        # Search using MULTILINGUAL keywords
        search_query = " ".join(rule['keywords'])
        relevant_docs = self.pdf_processor.search_documents(search_query, k=3)
        
        if not relevant_docs:
            return {
                'rule_id': rule_id,
                'rule_title': rule['title'],
                'compliance_status': 'NOT_FOUND',
                'confidence': 0.0,
                'evidence': [],
                'suggestions': ['No matching clauses found in contract'],
                'retrieved_content': [],
                'risk_level': 'low'
            }
        
        # Prepare context
        context = "\n\n".join([doc['content'] for doc in relevant_docs])
        
        # Use RULE-SPECIFIC multilingual prompt
        prompt = f"""{rule['prompt']}

Rental Contract Context (DE/EN):
{context}

RESPOND STRICTLY IN ENGLISH JSON FORMAT:"""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON (handles Gemini's formatting)
            json_text = self._extract_json(response_text)
            analysis = json.loads(json_text)
            
            # Standardize output
            result = {
                'rule_id': rule_id,
                'rule_title': rule['title'],
                'compliance_status': analysis.get('compliance_status', 'PARTIAL'),
                'confidence': analysis.get('confidence', 0.7),
                'evidence': analysis.get('evidence', []),
                'suggestions': [analysis.get('text', str(analysis))],  # Fallback
                'retrieved_content': [{
                    'content': doc['content'][:200] + '...' if len(doc['content']) > 200 else doc['content'],
                    'source': doc['metadata']['filename'],
                    'similarity': doc['similarity']
                } for doc in relevant_docs],
                'risk_level': analysis.get('risk_level', 'low'),
                'extracted_data': analysis  # Raw Gemini output
            }
            
            return result
            
        except Exception as e:
            print(f"Error analyzing {rule_id}: {e}")
            return {
                'rule_id': rule_id,
                'rule_title': rule['title'],
                'compliance_status': 'ERROR',
                'confidence': 0.0,
                'suggestions': [f'Analysis error: {str(e)}'],
                'retrieved_content': [],
                'risk_level': 'low'
            }
    
    def _extract_json(self, text: str) -> str:
        """Extract JSON from Gemini response"""
        if '```json' in text:
            start = text.find('```json') + 7
            end = text.find('```', start)
            return text[start:end].strip()
        elif '{' in text:
            start = text.find('{')
            end = text.rfind('}') + 1
            return text[start:end]
        return text
    
    def run_full_compliance_check(self) -> Dict[str, Any]:
        """Run check for current mode's rules"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'mode': self.mode,
            'total_rules': len(self.rules),
            'rule_results': {},
            'summary': {
                'compliant': 0, 'partial': 0, 'non_compliant': 0,
                'not_found': 0, 'errors': 0
            }
        }
        
        print(f"🔍 Analyzing {self.mode} contract ({len(self.rules)} rules)...")
        
        for i, rule in enumerate(self.rules, 1):
            print(f"  {i}/{len(self.rules)} {rule['rule_id']}")
            rule_result = self.check_rule_compliance(rule)
            results['rule_results'][rule_result['rule_id']] = rule_result
            
            # Update counters
            status = rule_result['compliance_status'].upper()
            if status == 'COMPLIANT':
                results['summary']['compliant'] += 1
            elif status == 'PARTIAL':
                results['summary']['partial'] += 1
            elif status == 'NON_COMPLIANT':
                results['summary']['non_compliant'] += 1
            elif status == 'NOT_FOUND':
                results['summary']['not_found'] += 1
            else:
                results['summary']['errors'] += 1
        
        # Save
        os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
        with open(RESULTS_FILE, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"✅ Done! Results: {RESULTS_FILE}")
        return results
    
    def get_rental_table(self) -> str:
        """Generate beautiful rental contract table (Markdown)"""
        try:
            with open(RESULTS_FILE, 'r') as f:
                results = json.load(f)
        except FileNotFoundError:
            return "❌ No results. Run `checker.run_full_compliance_check()` first."
        
        table_rows = []
        high_risk_issues = []
        
        for rule_id, result in results['rule_results'].items():
            status_emoji = {
                'COMPLIANT': '✅', 'PARTIAL': '⚠️', 'NOT_FOUND': '❓',
                'NON_COMPLIANT': '❌', 'ERROR': '🚨'
            }.get(result['compliance_status'].upper(), '❓')
            
            # Short summary
            summary = result['suggestions'][:80] + '...' if result['suggestions'] else 'No details'
            
            table_rows.append(f"| {status_emoji} | {result['rule_title'][:40]:<40} | {result['risk_level'].upper():<8} | {summary:<60} |")
            
            # Track high-risk issues
            if result.get('risk_level') == 'high':
                high_risk_issues.append(f"• {result['rule_title']}: {summary}")
        
        table = f"""
## 🏠 Rental Contract Analysis ({results['mode'].upper()})

| Status | Rule | Risk | Key Details |
|--------|------|------|-------------|
{table_rows}

**Overall Score**: {((results['summary']['compliant'] + results['summary']['partial'] * 0.5) / results['total_rules'] * 100):.0f}%"""

        if high_risk_issues:
            table += f"""

## 🚨 HIGH-RISK ISSUES
{chr(10).join(high_risk_issues)}
"""
        
        return table
    
    def print_table(self):
        """Print the rental table"""
        print(self.get_rental_table())


if __name__ == "__main__":
    # Rental contract analysis
    checker = ComplianceChecker(mode="rent")
    results = checker.run_full_compliance_check()
    print(checker.get_rental_table())