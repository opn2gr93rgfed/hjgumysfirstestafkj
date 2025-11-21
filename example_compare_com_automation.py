# ============================================
# EXAMPLE: Compare.com Auto Insurance Quote
# ============================================
# This is the user code to paste into the GUI editor
# It will be wrapped by smart_no_api provider with:
# - Octobrowser API profile management
# - Mandatory proxy support
# - Smart helper functions (smart_click, smart_fill, check_heading)
# - CSV data integration

# CSV Fields expected:
# Field 1 = ZIP Code
# Field 2 = Birth Month (MM)
# Field 3 = Birth Day (DD)
# Field 4 = Birth Year (YYYY)
# Field 5 = First Name
# Field 6 = Last Name
# Field 7 = Street Address
# Field 8 = Email Address
# Field 9 = Phone Number

# Navigate to Compare.com
page.goto("https://www.compare.com/")

# Enter ZIP code from CSV
smart_fill(page, [
    'role=textbox[name="Enter your ZIP code"]',
    'input[placeholder*="ZIP"]',
    '#zip-code-input'
], data_row.get('Field 1', '33071'), "ZIP Code", timeout=10000)

# Click "See My Quotes"
smart_click(page, [
    'role=button[name="See My Quotes"]',
    'button:has-text("See My Quotes")',
    'button:has-text("Get Quotes")'
], "See My Quotes Button")

# Question 1: Are you currently insured?
check_heading(page, ["Are you currently insured?", "Currently insured?"])
smart_click(page, [
    'role=button[name="No"]',
    'button:has-text("No"):visible'
], "Not Insured - No")

# Question 2: When do you plan to purchase?
check_heading(page, ["When do you plan to purchase", "Purchase timeline"])
smart_click(page, [
    'role=button[name="More than a month from now"]',
    'button:has-text("More than a month")',
    'button:has-text("month from now")'
], "Purchase Timeline")

# Question 3: Do you own or rent?
check_heading(page, ["Do you own or rent your home?", "Home ownership"])
smart_click(page, [
    'role=button[name="Own"]',
    'button:has-text("Own"):visible'
], "Home Owner - Own")

# Question 4: Car Year
check_heading(page, ["What's your car year?", "Car year", "Vehicle year"])
smart_click(page, [
    'role=button[name="2017"]',
    'button:has-text("2017")'
], "Car Year - 2017")

# Question 5: Car Make
check_heading(page, ["What's your car make?", "Car make", "Vehicle make"])
smart_click(page, [
    'role=button[name="Ford icon Ford"]',
    'button:has-text("Ford")',
    'button[aria-label*="Ford"]'
], "Car Make - Ford")

# Question 6: Car Model
check_heading(page, ["What's your car model?", "Car model", "Vehicle model"])
smart_click(page, [
    'role=button[name="Edge"]',
    'button:has-text("Edge")'
], "Car Model - Edge")

# Question 7: Car Trim
check_heading(page, ["What's your car trim?", "Car trim"])
smart_click(page, [
    'role=button[name="I don\'t know"]',
    'button:has-text("don\'t know")',
    'button:has-text("Unknown")'
], "Car Trim - Don't Know")

# Question 8: Body Style
check_heading(page, ["What's your car body style?", "Body style"])
smart_click(page, [
    'role=button[name="I don\'t know"]',
    'button:has-text("don\'t know")'
], "Body Style - Don't Know")

# Question 9: Main Use
check_heading(page, ["What's the main use of your", "Main use", "Primary use"])
smart_click(page, [
    'role=button[name="Commuting or personal use"]',
    'button:has-text("Commuting")',
    'button:has-text("personal use")'
], "Main Use - Commuting")

# Question 10: Miles Driven
check_heading(page, ["How many miles do you drive", "Annual mileage"])
smart_click(page, [
    'role=button[name="Miles National average"]',
    'button:has-text("National average")',
    'button:has-text("Average")'
], "Mileage - National Average")

# Question 11: Own or Lease
check_heading(page, ["Do you own or lease this car?", "Ownership status"])
smart_click(page, [
    'role=button[name="Owned"]',
    'button:has-text("Owned"):visible'
], "Ownership - Owned")

# Question 12: Include Coverage
check_heading(page, ["Would you like to include", "Include coverage"])
smart_click(page, [
    'role=button[name="No"]',
    'button:has-text("No"):visible'
], "Include Coverage - No")

# Question 13: Add Another Vehicle
check_heading(page, ["Would you like to add another", "Add another vehicle"])
smart_click(page, [
    'role=button[name="No"]',
    'button:has-text("No"):visible'
], "Add Another Vehicle - No")

# Question 14: Date of Birth
check_heading(page, ["What's your date of birth?", "Date of birth", "DOB"])

smart_fill(page, [
    'role=textbox[name="MM"]',
    'input[placeholder="MM"]',
    'input[name*="month"]'
], data_row.get('Field 2', '10'), "Birth Month")

smart_fill(page, [
    'role=textbox[name="DD"]',
    'input[placeholder="DD"]',
    'input[name*="day"]'
], data_row.get('Field 3', '31'), "Birth Day")

smart_fill(page, [
    'role=textbox[name="YYYY"]',
    'input[placeholder="YYYY"]',
    'input[name*="year"]'
], data_row.get('Field 4', '1963'), "Birth Year")

smart_click(page, [
    'role=button[name="Next"]',
    'button:has-text("Next")',
    'button:has-text("Continue")'
], "Next Button")

# Question 15: Gender
check_heading(page, ["What's your gender?", "Gender"])
smart_click(page, [
    'role=button[name="Female"]',
    'button:has-text("Female")'
], "Gender - Female")

# Question 16: Active U.S. License
check_heading(page, ["Do you have an active U.S.", "Active license", "U.S. driver's license"])
smart_click(page, [
    'role=button[name="Yes"]',
    'button:has-text("Yes"):visible'
], "Active License - Yes")

# Question 17: Age When Licensed
check_heading(page, ["How old were you when you", "Licensed age"])
smart_click(page, [
    'role=button[name="16"]',
    'button:has-text("16")'
], "Licensed Age - 16")

# Question 18: Credit Score
check_heading(page, ["What's your credit score?", "Credit score"])
smart_click(page, [
    'role=button[name="Excellent (720+)"]',
    'button:has-text("Excellent")',
    'button:has-text("720+")'
], "Credit Score - Excellent")

# Question 19: Education Level
check_heading(page, ["What's your highest level of", "Education level", "Highest education"])
smart_click(page, [
    'role=button[name="High School/GED"]',
    'button:has-text("High School")',
    'button:has-text("GED")'
], "Education - High School")

# Question 20: Military Service
check_heading(page, ["Have you or an immediate", "Military service"])
smart_click(page, [
    'role=button[name="No"]',
    'button:has-text("No"):visible'
], "Military - No")

# Question 21: Special Conditions
check_heading(page, ["Do any of these apply to you?", "Special conditions"])
smart_click(page, [
    'role=button[name="Continue"]',
    'button:has-text("Continue")'
], "Continue Button")

# Question 22: Bundle Insurance
check_heading(page, ["Would you also like to", "Bundle insurance"])
smart_click(page, [
    'role=button[name="No"]',
    'button:has-text("No"):visible'
], "Bundle - No")

# Question 23: Why No Insurance
check_heading(page, ["Why don't you have insurance?", "No insurance reason"])
smart_click(page, [
    'role=button[name="My policy expired"]',
    'button:has-text("expired")',
    'button:has-text("Policy expired")'
], "Reason - Expired")

# Question 24: Time Since Insurance
check_heading(page, ["How long has it been since", "Time without insurance"])
smart_click(page, [
    'role=button[name="More than a month"]',
    'button:has-text("More than a month")'
], "Time Since - More Than Month")

# Question 25: At-Fault Accidents
check_heading(page, ["How many at-fault accidents", "At-fault accidents"])
smart_click(page, [
    'role=button[name="0"]',
    'button:has-text("0"):visible'
], "Accidents - 0")

# Question 26: Speeding Tickets
check_heading(page, ["How many speeding tickets", "Speeding tickets"])
smart_click(page, [
    'role=button[name="0"]',
    'button:has-text("0"):visible'
], "Speeding Tickets - 0")

# Question 27: Insurance Claims
check_heading(page, ["How many insurance claims", "Insurance claims"])
smart_click(page, [
    'role=button[name="0"]',
    'button:has-text("0"):visible'
], "Claims - 0")

# Question 28: DUI/DWI
check_heading(page, ["How many DUI/DWI convictions", "DUI convictions"])
smart_click(page, [
    'role=button[name="0"]',
    'button:has-text("0"):visible'
], "DUI - 0")

# Question 29: SR-22
check_heading(page, ["Do you require an SR-22", "SR-22 requirement"])
smart_click(page, [
    'role=button[name="No Common choice"]',
    'button:has-text("No")',
    'button:has-text("Common choice")'
], "SR-22 - No")

# Question 30: Wrap Up - Name
check_heading(page, ["You're so close! Let's wrap", "Final details", "Wrap up"])

smart_fill(page, [
    'role=textbox[name="First name"]',
    'input[placeholder*="First"]',
    'input[name*="first"]'
], data_row.get('Field 5', 'Janice'), "First Name")

smart_fill(page, [
    'role=textbox[name="Last name"]',
    'input[placeholder*="Last"]',
    'input[name*="last"]'
], data_row.get('Field 6', 'North'), "Last Name")

smart_click(page, [
    'role=button[name="Next"]',
    'button:has-text("Next")'
], "Next Button")

# Question 31: Add Another Driver
check_heading(page, ["Would you like to add another", "Add another driver"])
smart_click(page, [
    'role=button[name="No"]',
    'button:has-text("No"):visible'
], "Add Driver - No")

# Question 32: Parking Location
check_heading(page, ["Where do you park your car", "Parking location", "Car parking"])

smart_fill(page, [
    'role=textbox[name="Enter location"]',
    'input[placeholder*="location"]',
    'input[placeholder*="address"]'
], data_row.get('Field 7', '1545'), "Parking Address")

# Wait for autocomplete and select first option
time.sleep(1)
page.keyboard.press("ArrowDown")
page.keyboard.press("Enter")

smart_click(page, [
    'role=button[name="Next"]',
    'button:has-text("Next")'
], "Next Button")

# Question 33: Email Address
check_heading(page, ["Where would you like to", "Email address", "Contact email"])

smart_fill(page, [
    'role=textbox[name="Email address"]',
    'input[type="email"]',
    'input[placeholder*="email"]'
], data_row.get('Field 8', 'test@example.com'), "Email Address")

smart_click(page, [
    'role=button[name="Next"]',
    'button:has-text("Next")'
], "Next Button")

# Question 34: Phone Number
check_heading(page, ["One final step", "Phone number", "Contact phone"])

smart_fill(page, [
    'role=textbox[name="Phone number"]',
    'input[type="tel"]',
    'input[placeholder*="phone"]'
], data_row.get('Field 9', '(714) 829-9472'), "Phone Number")

# Final Submit
smart_click(page, [
    'role=button[name="View my quotes"]',
    'button:has-text("View my quotes")',
    'button:has-text("Get quotes")'
], "View Quotes Button")

# Wait for results page
time.sleep(3)

print(f"[SUCCESS] Quote flow completed for {data_row.get('Field 5', 'Unknown')}")
