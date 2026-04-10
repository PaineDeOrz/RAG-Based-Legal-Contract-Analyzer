import streamlit as st
import json
import os
from compliance_checker import ComplianceChecker
from pdf_processor import PDFProcessor
from compliance_rules import get_rules  # ← CHANGED: mode-aware
from config import RESULTS_FILE


# Page configuration - RENTAL EDITION 🏠
st.set_page_config(
    page_title="Rental Contract Analyzer",
    page_icon="🏠",
    layout="wide"
)


def initialize_system(mode: str = "rent"):  # ← CHANGED: mode parameter
    """Initialize rental contract analyzer"""
    try:
        with st.spinner("Initializing rental analyzer..."):
            processor = PDFProcessor()
            
            # FAILS if no real contracts (no sample generation)
            if not os.path.exists("data/pdfs") or not os.listdir("data/pdfs"):
                st.error("❌ **No rental contracts found!**\n\n"
                        "1. Create `data/pdfs/` folder\n"
                        "2. Add `Contract1.pdf` (or any rental contract)\n"
                        "3. Refresh page")
                st.stop()
            
            processor.load_vector_store()
            checker = ComplianceChecker(mode=mode)  # ← CHANGED: rental mode
            
            st.success(f"✅ Rental analyzer ready! Found {len(os.listdir('data/pdfs'))} contract(s)")
            return checker
            
    except Exception as e:
        st.error(f"❌ Rental analyzer failed: {e}")
        return None


def main():
    st.title("🏠 Rental Contract Compliance Analyzer")
    st.markdown("""
    **AI-powered analysis of rental contracts** (German/English). 
    Extracts rent, deposit, termination rules, and flags risks automatically.
    """)
    
    # Initialize rental system
    checker = initialize_system("rent")
    if checker is None:
        st.stop()
    
    # Sidebar - Rental info
    with st.sidebar:
        st.header("🏠 Rental Contracts")
        
        # Contract files
        pdf_files = [f for f in os.listdir("data/pdfs") if f.endswith(('.pdf', '.txt'))]
        st.metric("📄 Contracts", len(pdf_files))
        
        with st.expander("Contract Files"):
            for file in pdf_files:
                st.write(f"• **{file}**")
        
        # Rental rules info
        rules = get_rules("rent")  # ← CHANGED
        st.metric("📋 Rental Rules", len(rules))
        st.info(f"**Analyzes:** Rent, Deposit, Termination, House Rules, etc.")
        
        st.markdown("---")
        st.markdown("**Powered by Gemini 2.5**")
    
    # Main tabs - Rental focused
    tab1, tab2, tab3 = st.tabs(["🔍 Analyze Contract", "📊 Rental Table", "🔎 Search Contract"])
    
    with tab1:
        st.header("🔍 Run Rental Analysis")
        st.info("Analyzes your rental contract for key terms and risks.")
        
        if st.button("🚀 Analyze Rental Contract", type="primary"):
            with st.spinner("Analyzing rent, deposit, termination rules..."):
                try:
                    results = checker.run_full_compliance_check()
                    st.success("✅ Rental analysis complete!")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Analysis failed: {e}")
    
    with tab2:
        st.header("📊 Rental Contract Summary")
        
        if os.path.exists(RESULTS_FILE):
            try:
                with open(RESULTS_FILE, 'r') as f:
                    results = json.load(f)
                
                # Rental metrics
                summary = results['summary']
                total = results['total_rules']
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("✅ Found", summary['compliant'] + summary['partial'], 
                             f"{(summary['compliant'] + summary['partial'])/total*100:.0f}%")
                with col2:
                    st.metric("❓ Missing", summary['not_found'], 
                             f"{summary['not_found']/total*100:.0f}%")
                with col3:
                    st.metric("🚨 High Risk", 
                             sum(1 for r in results['rule_results'].values() if r.get('risk_level') == 'high'),
                             "0")
                with col4:
                    score = (summary['compliant'] + summary['partial'] * 0.7) / total * 100
                    st.metric("🏠 Safety Score", f"{score:.0f}%", delta=None)
                
                # Rental table (from checker)
                st.markdown("### 📋 Key Rental Terms")
                st.markdown(checker.get_rental_table().strip())  # ← NEW: beautiful table
                
            except Exception as e:
                st.error(f"Error loading results: {e}")
        else:
            st.info("👆 Run analysis first!")
    
    with tab3:
        st.header("🔎 Search Rental Contract")
        st.info("Find specific clauses (works in German/English)")
        
        search_query = st.text_input("Search terms:", 
                                   placeholder="Kaution, Miete €450, Kündigung, deposit, rent")
        
        if search_query:
            with st.spinner("Searching contract..."):
                processor = PDFProcessor()
                processor.load_vector_store()
                results = processor.search_documents(search_query, k=5)
                
                if results:
                    st.success(f"Found {len(results)} matching sections:")
                    for i, result in enumerate(results, 1):
                        with st.expander(f"📄 {result['metadata']['filename']} (Score: {result['similarity']:.1%})"):
                            st.write(result['content'][:1000])
                else:
                    st.info("No matching clauses found.")


if __name__ == "__main__":
    main()