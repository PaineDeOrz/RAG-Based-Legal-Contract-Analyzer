import json
import os
from compliance_checker import ComplianceChecker
from pdf_processor import PDFProcessor
from config import RESULTS_FILE


def run_evaluation(mode: str = "rent"):
    """Evaluate rental contract compliance system"""
    print("=" * 60)
    print(f"🏠 RENTAL CONTRACT ANALYZER EVALUATION ({mode.upper()})")
    print("=" * 60)
    
    # Initialize system
    print("\n1. Initializing rental analyzer...")
    try:
        checker = ComplianceChecker(mode=mode)  # ← NEW: mode parameter
        print("✓ Rental compliance checker initialized")
        
        processor = PDFProcessor()
        processor.load_vector_store()
        print("✓ PDF processor + multilingual vector store loaded")
        
    except Exception as e:
        print(f"❌ Error initializing: {e}")
        return
    
    # Test RENTAL-SPECIFIC document search
    print("\n2. Testing rental contract search...")
    rental_queries = [  # ← NEW: rental keywords (DE/EN)
        "Kaution deposit €600", "Benützungsentgelt rent €450", "Kündigung termination",
        "von bis Vertragsdauer", "Wehlistraße Handelskai", "zweimonatig notice period"
    ]
    
    search_results = {}
    for query in rental_queries:
        try:
            results = processor.search_documents(query, k=3)
            search_results[query[:30] + "..."] = len(results)  # Truncate for display
            print(f"✓ '{query[:25]}...': {len(results)} docs found")
        except Exception as e:
            print(f"❌ '{query[:25]}...': Error - {e}")
            search_results[query[:30] + "..."] = 0
    
    # Run rental compliance analysis
    print("\n3. Running rental contract analysis...")
    try:
        results = checker.run_full_compliance_check()
        print("✓ Rental analysis completed!")
        
        # Rental-specific summary
        summary = results['summary']
        total = results['total_rules']
        
        print(f"\n📊 RENTAL CONTRACT RESULTS:")
        print(f"✓ Rules analyzed: {total}")
        print(f"✓ Found clauses: {summary['compliant'] + summary['partial']} ({(summary['compliant'] + summary['partial'])/total*100:.1f}%)")
        print(f"✓ Missing clauses: {summary['not_found']} ({summary['not_found']/total*100:.1f}%)")
        
        rental_score = (summary['compliant'] + summary['partial'] * 0.7) / total * 100  # Rental weighting
        print(f"✓ Rental safety score: {rental_score:.1f}%")
        
    except Exception as e:
        print(f"❌ Rental analysis failed: {e}")
        return
    
    # Show top rental findings
    print("\n4. 🏠 KEY RENTAL FINDINGS:")
    rental_rules = ['contract_duration', 'rent_amount', 'deposit_details', 'termination_tenant']
    for rule_id in rental_rules:
        if rule_id in results['rule_results']:
            result = results['rule_results'][rule_id]
            status = result['compliance_status']
            details = result['suggestions'][0][:60] + "..." if result['suggestions'] else "No details"
            print(f"  • {result['rule_title'][:35]:<35} {status:<12} {details}")
    
    # Generate evaluation report
    print("\n5. 📈 System evaluation report...")
    
    evaluation_report = {
        'timestamp': results['timestamp'],
        'mode': mode,
        'system_performance': {
            'search_success_rate': sum(1 for count in search_results.values() if count > 0) / len(search_results),
            'documents_processed': len(set(meta['filename'] for meta in processor.chunk_metadata)),
            'chunks_created': len(processor.document_chunks),
            'rental_rules_analyzed': total,
            'successful_analyses': sum(1 for r in results['rule_results'].values() if r['compliance_status'] != 'ERROR')
        },
        'rental_metrics': {
            'safety_score': rental_score,
            'critical_clauses_found': sum(1 for rule_id in ['rent_amount', 'deposit_details', 'termination_tenant'] 
                                       if rule_id in results['rule_results'] and 
                                       results['rule_results'][rule_id]['compliance_status'] != 'NOT_FOUND'),
            'high_risk_issues': sum(1 for r in results['rule_results'].values() if r.get('risk_level') == 'high')
        },
        'search_tests': search_results,
        'recommendations': generate_rental_recommendations(results, mode)
    }
    
    # Save report
    eval_file = os.path.join('data', f'{mode}_evaluation_report.json')
    os.makedirs('data', exist_ok=True)
    with open(eval_file, 'w') as f:
        json.dump(evaluation_report, f, indent=2)
    
    print(f"✓ Report saved: {eval_file}")
    
    # Final assessment
    print("\n" + "=" * 60)
    print("🏠 RENTAL ANALYZER ASSESSMENT")
    print("=" * 60)
    
    perf = evaluation_report['system_performance']
    print(f"📄 Contracts processed: {perf['documents_processed']}")
    print(f"🔍 Search accuracy: {perf['search_success_rate']*100:.1f}%")
    print(f"📋 Rental clauses found: {evaluation_report['rental_metrics']['critical_clauses_found']}/4")
    
    if rental_score >= 85:
        print("\n✅ EXCELLENT: Safe rental contract")
    elif rental_score >= 70:
        print("\n✅ GOOD: Generally safe, minor concerns")
    elif rental_score >= 55:
        print("\n⚠️  CAUTION: Several missing clauses")
    else:
        print("\n❌ RISK: Major clauses missing - review carefully!")
    
    print("\n📋 Run `checker.print_table()` for full rental table!")
    return evaluation_report


def generate_rental_recommendations(results, mode):
    """Rental-specific recommendations"""
    recommendations = []
    summary = results['summary']
    
    if summary['not_found'] > 2:
        recommendations.append(f"❌ {summary['not_found']} critical rental clauses missing")
    
    high_risk = [r for r in results['rule_results'].values() if r.get('risk_level') == 'high']
    if high_risk:
        recommendations.append(f"🚨 Review {len(high_risk)} high-risk clauses")
    
    # Contract1.pdf specific
    if 'rent_amount' in results['rule_results'] and results['rule_results']['rent_amount']['compliance_status'] == 'FOUND':
        recommendations.append("💰 Rent amount clearly defined ✓")
    
    if 'deposit_details' in results['rule_results']:
        deposit_result = results['rule_results']['deposit_details']
        if deposit_result['compliance_status'] != 'NOT_FOUND':
            recommendations.append("🏦 Deposit terms specified ✓")
    
    recommendations.append("📋 View full table: `checker.get_rental_table()`")
    return recommendations


if __name__ == "__main__":
    evaluation_report = run_evaluation("rent")
    print("\n🎉 Rental analyzer evaluation complete!")