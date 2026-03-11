"""
FL Tax Shield — Florida Sales Tax Calculator + Quarterly Estimator
MVP v0.1 | Not tax advice — consult CPA
"""

# Florida Sales Tax Rates by County (2026)
# Source: SalesTaxHandbook.com, updated March 2026
COUNTY_TAX_RATES = {
    # Major Metro Areas
    "Miami-Dade": 0.07,
    "Broward": 0.07,
    "Palm Beach": 0.07,
    "Hillsborough": 0.075,
    "Pinellas": 0.075,
    "Orange": 0.075,
    "Lee": 0.065,
    
    # Other Counties
    "Alachua": 0.085,  # Highest in state (Gainesville)
    "Baker": 0.07,
    "Bay": 0.075,
    "Bradford": 0.075,
    "Brevard": 0.07,
    "Calhoun": 0.075,
    "Charlotte": 0.07,
    "Citrus": 0.065,
    "Clay": 0.075,
    "Collier": 0.075,
    "Columbia": 0.075,
    "Desoto": 0.075,
    "Dixie": 0.07,
    "Duval": 0.075,
    "Escambia": 0.075,
    "Flagler": 0.07,
    "Franklin": 0.075,
    "Gadsden": 0.075,
    "Gilchrist": 0.075,
    "Glades": 0.075,
    "Gulf": 0.075,
    "Hamilton": 0.08,
    "Hardee": 0.075,
    "Hendry": 0.075,
    "Hernando": 0.07,
    "Highlands": 0.075,
    "Holmes": 0.075,
    "Indian River": 0.07,
    "Jackson": 0.075,
    "Jefferson": 0.075,
    "Lafayette": 0.075,
    "Lake": 0.075,
    "Leon": 0.075,
    "Levy": 0.075,
    "Liberty": 0.07,
    "Madison": 0.08,
    "Manatee": 0.07,
    "Marion": 0.075,
    "Martin": 0.07,
    "Monroe": 0.075,
    "Nassau": 0.075,
    "Okaloosa": 0.07,
    "Okeechobee": 0.075,
    "Osceola": 0.075,
    "Pasco": 0.075,
    "Polk": 0.075,
    "Putnam": 0.075,
    "Santa Rosa": 0.075,
    "Sarasota": 0.07,
    "Seminole": 0.07,
    "St. Johns": 0.075,
    "St. Lucie": 0.07,
    "Sumter": 0.075,
    "Suwannee": 0.075,
    "Taylor": 0.07,
    "Union": 0.07,
    "Volusia": 0.07,
    "Wakulla": 0.075,
    "Walton": 0.075,
    "Washington": 0.075,
}

# Business type sales tax exemptions (partial)
# In FL, some services are exempt, some aren't
# Source: FL Dept of Revenue, general guidance
TAXABLE_SERVICES = {
    "restaurant": 1.0,        # 100% taxable (food + service)
    "retail": 1.0,            # 100% taxable (merchandise)
    "salon": 1.0,             # 100% taxable (services)
    "spa": 1.0,               # 100% taxable
    "cleaning": 0.6,          # 60% taxable (some exemption on labor)
    "lawncare": 0.0,          # 0% (agricultural exemption often applies)
    "landscaping": 0.0,       # 0% (agricultural exemption)
    "contractor": 0.0,        # 0% (labor exempt, materials taxable - complex)
    "consulting": 0.0,        # 0% (professional services exempt)
    "real_estate": 0.0,       # 0% (professional services exempt)
    "medical": 0.0,           # 0% (medical services exempt)
    "legal": 0.0,             # 0% (legal services exempt)
    "accounting": 0.0,        # 0% (professional services exempt)
    "e-commerce": 1.0,        # 100% taxable (if selling tangible goods)
    "dropshipping": 1.0,      # 100% taxable
    "hotel": 1.0,             # 100% (lodging + tax)
    "short_term_rental": 1.0, # 100% (vacation rentals taxable)
    "gym": 1.0,               # 100% (memberships taxable)
    "subscriptions": 1.0,     # 100% (digital goods taxable)
    "other": 0.5,             # 50% default assumption
}

# FL Corporate Income Tax Rates (2026)
# Florida has a 5.5% corporate income tax on C-corps
# S-corps, LLCs, sole props are pass-through (no FL income tax)
CORPORATE_TAX_RATE = 0.055

# Discount rates for early filing (FL allows this)
EARLY_FILING_DISCOUNT = 0.005  # 0.5% discount if filed by 1st of month

# Collection allowance (FL allows businesses to keep 2.5% of tax due, max $30)
COLLECTION_ALLOWANCE_RATE = 0.025
COLLECTION_ALLOWANCE_MAX = 30.00

# Business structures (affects quarterly estimate logic)
BUSINESS_STRUCTURES = {
    "sole_prop": {
        "income_tax": "pass_through",
        "quarterly_due": "estimated_tax",
    },
    "LLC": {
        "income_tax": "pass_through",
        "quarterly_due": "estimated_tax",
    },
    "S_corp": {
        "income_tax": "pass_through",
        "quarterly_due": "estimated_tax",
    },
    "C_corp": {
        "income_tax": "corporate",
        "quarterly_due": "form_1120",
    },
}

def get_county_rate(county: str) -> float:
    """Get sales tax rate for a county."""
    return COUNTY_TAX_RATES.get(county, 0.06)  # Default to 6% state minimum


def calculate_sales_tax(annual_revenue: float, county: str, business_type: str) -> dict:
    """
    Calculate estimated Florida sales tax owed.
    
    Args:
        annual_revenue: Gross annual revenue
        county: Florida county name
        business_type: Type of business
    
    Returns:
        Dictionary with tax breakdown
    """
    rate = get_county_rate(county)
    taxable_ratio = TAXABLE_SERVICES.get(business_type.lower(), 0.5)
    
    # Estimated taxable revenue (some services exempt)
    taxable_revenue = annual_revenue * taxable_ratio
    
    # Annual sales tax owed
    annual_tax = taxable_revenue * rate
    
    # Monthly and quarterly breakdown
    monthly_tax = annual_tax / 12
    quarterly_tax = annual_tax / 4
    
    return {
        "county": county,
        "tax_rate": rate,
        "business_type": business_type,
        "taxable_ratio": taxable_ratio,
        "annual_revenue": annual_revenue,
        "taxable_revenue": taxable_revenue,
        "annual_sales_tax": round(annual_tax, 2),
        "monthly_sales_tax": round(monthly_tax, 2),
        "quarterly_sales_tax": round(quarterly_tax, 2),
    }


def calculate_corporate_tax(annual_revenue: float, structure: str) -> dict:
    """
    Calculate estimated Florida corporate income tax.
    Only applies to C-corps. S-corps, LLCs, sole props are pass-through.
    """
    if structure.upper() in ["C_CORP", "C-CORP", "C CORP"]:
        # Assume 10% net profit margin for estimation (conservative)
        estimated_profit = annual_revenue * 0.10
        annual_corporate_tax = estimated_profit * CORPORATE_TAX_RATE
        quarterly_corporate_tax = annual_corporate_tax / 4
        
        return {
            "structure": "C-Corp",
            "estimated_profit": estimated_profit,
            "tax_rate": CORPORATE_TAX_RATE,
            "annual_corporate_tax": round(annual_corporate_tax, 2),
            "quarterly_corporate_tax": round(quarterly_corporate_tax, 2),
            "note": "Based on estimated 10% profit margin. Consult CPA for actual."
        }
    else:
        return {
            "structure": structure,
            "estimated_profit": 0,
            "tax_rate": 0,
            "annual_corporate_tax": 0,
            "quarterly_corporate_tax": 0,
            "note": "Pass-through entity (LLC/S-corp/Sole Prop). No FL corporate tax."
        }


def calculate_collection_allowance(annual_tax: float) -> dict:
    """
    FL allows businesses to keep 2.5% of sales tax collected, max $30/filing location.
    This is the "collection allowance" for timely filing.
    """
    allowance = min(annual_tax * COLLECTION_ALLOWANCE_RATE, COLLECTION_ALLOWANCE_MAX * 4)  # 4 filings/year
    # Actually, it's per filing - so up to $30 x 4 = $120/year if filing monthly
    # For simplicity, let's show the quarterly version
    allowance_per_filing = min(annual_tax * COLLECTION_ALLOWANCE_RATE / 4, COLLECTION_ALLOWANCE_MAX)
    
    return {
        "annual_allowance": round(allowance, 2),
        "per_filing_allowance": round(allowance_per_filing, 2),
        "note": "FL allows keeping 2.5% of tax due (max $30) per filing period for timely filing."
    }


def generate_report(revenue: float, county: str, structure: str, business_type: str) -> str:
    """Generate a formatted tax report with sales tax + corporate tax + allowances."""
    calc = calculate_sales_tax(revenue, county, business_type)
    corp_tax = calculate_corporate_tax(revenue, structure)
    allowance = calculate_collection_allowance(calc['annual_sales_tax'])
    
    # Total estimated tax
    total_annual = calc['annual_sales_tax'] + corp_tax['annual_corporate_tax'] - allowance['annual_allowance']
    total_quarterly = calc['quarterly_sales_tax'] + corp_tax['quarterly_corporate_tax'] - allowance['per_filing_allowance']
    
    report = f"""
╔══════════════════════════════════════════════════════════════╗
║              FL TAX SHIELD — Tax Estimate Report              ║
╠══════════════════════════════════════════════════════════════╣
║ BUSINESS: {business_type.upper():<48} ║
║ STRUCTURE: {structure.upper():<46} ║
║ COUNTY: {county:<55} ║
╚══════════════════════════════════════════════════════════════╝

📊 REVENUE & TAXABLE BASE
──────────────────────────────────────────────────────────────
  Annual Revenue:        ${revenue:>12,.2f}
  Taxable Ratio:         {calc['taxable_ratio']:>12.0%}
  Taxable Revenue:       ${calc['taxable_revenue']:>12,.2f}

💰 FLORIDA SALES TAX
──────────────────────────────────────────────────────────────
  Tax Rate ({county}):     {calc['tax_rate']*100:>10.1f}%
  Annual Sales Tax:       ${calc['annual_sales_tax']:>12,.2f}
  Monthly Estimate:       ${calc['monthly_sales_tax']:>12,.2f}
  Quarterly Payments:     ${calc['quarterly_sales_tax']:>12,.2f}

📅 QUARTERLY PAYMENT SCHEDULE
──────────────────────────────────────────────────────────────
  Q1 (Apr 15):            ${calc['quarterly_sales_tax']:>12,.2f}
  Q2 (Jun 15):            ${calc['quarterly_sales_tax']:>12,.2f}
  Q3 (Sep 15):            ${calc['quarterly_sales_tax']:>12,.2f}
  Q4 (Jan 15):            ${calc['quarterly_sales_tax']:>12,.2f}

⚠️  DISCLAIMER
──────────────────────────────────────────────────────────────
  This is an ESTIMATE only. Florida sales tax rules are complex
  and vary by specific business activity. Some services may be
  partially or fully exempt. Consult a CPA before filing.
  
  For official rates: floridarevenue.com/taxes/sales
"""
    return report


# ─────────────────────────────────────────────────────────────────
# Example Usage
# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Example 1: Restaurant in Miami-Dade
    print("=" * 60)
    print("EXAMPLE 1: Restaurant in Miami-Dade, $200k revenue")
    print("=" * 60)
    print(generate_report(200000, "Miami-Dade", "LLC", "restaurant"))
    
    # Example 2: Cleaning business in Orange County (Orlando)
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Cleaning business in Orange County, $75k")
    print("=" * 60)
    print(generate_report(75000, "Orange", "sole_prop", "cleaning"))
    
    # Example 3: Retail store in Broward
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Retail store in Broward, $350k revenue")
    print("=" * 60)
    print(generate_report(350000, "Broward", "LLC", "retail"))