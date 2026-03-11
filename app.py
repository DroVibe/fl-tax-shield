"""
FL Tax Shield — Streamlit UI
Florida Sales Tax Calculator & Quarterly Estimator
"""

import streamlit as st
from calculator import (
    COUNTY_TAX_RATES,
    TAXABLE_SERVICES,
    calculate_sales_tax,
    calculate_corporate_tax,
    calculate_collection_allowance,
)

# Page config
st.set_page_config(
    page_title="FL Tax Shield",
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1e3a5f;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c5282;
    }
    .tax-card {
        background-color: #f7fafc;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #3182ce;
        margin: 1rem 0;
    }
    .disclaimer {
        background-color: #fffaf0;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #dd6b20;
        font-size: 0.9rem;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2d3748;
    }
    .highlight {
        color: #e53e3e;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">🛡️ FL Tax Shield</p>', unsafe_allow_html=True)
st.markdown("### Florida Sales Tax Calculator & Quarterly Estimator")
st.markdown("---")

# Sidebar - Input Section
with st.sidebar:
    st.header("📋 Business Details")
    
    # County selection
    counties = sorted(COUNTY_TAX_RATES.keys())
    selected_county = st.selectbox(
        "Select Florida County",
        counties,
        index=counties.index("Miami-Dade") if "Miami-Dade" in counties else 0,
        help="Select your business location in Florida"
    )
    
    # Business type selection (only show the main 9 as mentioned)
    business_types = [
        "restaurant", "retail", "salon", "spa", 
        "cleaning", "lawncare", "contractor", "consulting", "other"
    ]
    selected_business = st.selectbox(
        "Business Type",
        business_types,
        index=0,
        help="Affects taxable revenue ratio"
    )
    
    # Monthly revenue input
    monthly_revenue = st.number_input(
        "Monthly Revenue ($)",
        min_value=0.0,
        max_value=100_000_000.0,
        value=10000.0,
        step=500.0,
        format="%.2f"
    )
    
    # Annualize
    annual_revenue = monthly_revenue * 12
    
    st.markdown("---")
    st.markdown(f"**Annual Revenue:** ${annual_revenue:,.2f}")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📊 Tax Breakdown")
    
    if monthly_revenue > 0:
        # Calculate taxes
        sales_tax = calculate_sales_tax(annual_revenue, selected_county, selected_business)
        corp_tax = calculate_corporate_tax(annual_revenue, "LLC")  # Default to LLC
        allowance = calculate_collection_allowance(sales_tax['annual_sales_tax'])
        
        # Display main metrics
        st.markdown('<div class="tax-card">', unsafe_allow_html=True)
        
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric(
                "Monthly Sales Tax",
                f"${sales_tax['monthly_sales_tax']:,.2f}",
                help=f"Based on {sales_tax['tax_rate']*100:.1f}% rate in {selected_county}"
            )
        with m2:
            st.metric(
                "Quarterly Estimate",
                f"${sales_tax['quarterly_sales_tax']:,.2f}",
                help="Due April 15, June 15, Sept 15, Jan 15"
            )
        with m3:
            st.metric(
                "Annual Sales Tax",
                f"${sales_tax['annual_sales_tax']:,.2f}",
                delta=f"Taxable: ${sales_tax['taxable_revenue']:,.0f}",
                delta_color="off"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Detailed breakdown
        st.markdown("### 📋 Detailed Breakdown")
        
        with st.expander("View Full Breakdown", expanded=True):
            st.write(f"**County:** {selected_county}")
            st.write(f"**Tax Rate:** {sales_tax['tax_rate']*100:.1f}%")
            st.write(f"**Business Type:** {selected_business.title()}")
            st.write(f"**Taxable Ratio:** {sales_tax['taxable_ratio']*100:.0f}%")
            st.write(f"**Annual Revenue:** ${annual_revenue:,.2f}")
            st.write(f"**Taxable Revenue:** ${sales_tax['taxable_revenue']:,.2f}")
        
        # Quarterly schedule
        st.markdown("### 📅 Quarterly Payment Schedule")
        
        quarters = [
            ("Q1", "April 15", sales_tax['quarterly_sales_tax']),
            ("Q2", "June 15", sales_tax['quarterly_sales_tax']),
            ("Q3", "September 15", sales_tax['quarterly_sales_tax']),
            ("Q4", "January 15", sales_tax['quarterly_sales_tax']),
        ]
        
        for q, date, amount in quarters:
            st.write(f"**{q}** ({date}): ${amount:,.2f}")
        
        # Collection allowance
        st.markdown("### 💡 Collection Allowance")
        st.info(f"FL allows keeping 2.5% of tax collected (max $30) per filing = **${allowance['per_filing_allowance']:.2f}/quarter** if filed on time.")

with col2:
    st.markdown("### 🗺️ County Tax Rates")
    
    # Show rates for selected and nearby counties
    rate_data = []
    for county, rate in sorted(COUNTY_TAX_RATES.items(), key=lambda x: x[1], reverse=True):
        rate_data.append({"County": county, "Rate": f"{rate*100:.1f}%"})
    
    # Display top 10 rates
    st.dataframe(
        rate_data[:10],
        hide_index=True,
        use_container_width=True
    )
    
    with st.expander("All 67 Counties"):
        st.dataframe(
            rate_data,
            hide_index=True,
            use_container_width=True
        )

# Disclaimer
st.markdown("---")
st.markdown("""
<div class="disclaimer">
⚠️ <strong>DISCLAIMER:</strong> This tool provides ESTIMATES only. Florida sales tax rules are complex 
and vary by specific business activity. Some services may be partially or fully exempt. 
<strong>Consult a CPA</strong> before filing. For official rates, visit <a href="https://floridarevenue.gov/taxes/sales" target="_blank">Florida Department of Revenue</a>.
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("*FL Tax Shield v0.1 — Not tax advice. Consult a CPA.*")