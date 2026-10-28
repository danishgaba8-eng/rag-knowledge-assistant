# Evaluation results

Provider: Ollama (llama3.2 + nomic-embed-text)  
Questions: 36 (29 answerable, 7 restricted or out of scope)  
Run time: 273s

| Metric | Result |
|---|---|
| Retrieval hit rate (correct document in top 4) | 100% (29/29) |
| Answer accuracy (all expected facts present) | 97% (28/29) |
| Answers with citations | 83% (24/29) |
| Correct 'not found' on restricted or out-of-scope questions | 100% (7/7) |
| Restricted data leaks | 0 |

## Per question

| Result | Type | Role | Question | Answer |
|---|---|---|---|---|
| PASS | answerable | employee | How many days of paid annual leave do full-time employees get? | Full-time employees receive 22 days of paid annual leave per calendar year. |
| PASS | answerable | employee | How many unused leave days can I carry over, and by when must I use them? | You can carry over up to 5 unused annual leave days into the next year. [1] You must use these carried-over days by March 31. |
| PASS | answerable | employee | When do I need a medical certificate for sick leave? | You need a medical certificate for absences of more than 3 consecutive working days [1]. |
| PASS | answerable | employee | How long is parental leave for the primary caregiver? | The primary caregiver receives 16 weeks of fully paid parental leave. [1] |
| PASS | answerable | employee | How many bereavement days can I take for an immediate family member? | You may take up to 5 paid days of bereavement leave for an immediate family member. [1] |
| PASS | answerable | employee | What is the deadline for submitting an expense claim? | The deadline for submitting an expense claim is within 30 days of the expense date. [1] |
| PASS | answerable | employee | Above what amount do I need an itemised receipt? | You need an itemised receipt for every expense over $25 [1]. |
| PASS | answerable | employee | Who has to approve an expense claim of $1,500? | According to [1], claims above $1,000 must also be approved by the Finance Director. |
| PASS | answerable | employee | What is the daily meal allowance for international travel? | The daily meal allowance for international travel is $85 [1]. |
| PASS | answerable | employee | What is the mileage rate for using my own car? | The mileage rate for using your own car is $0.42 per kilometre. |
| PASS | answerable | employee | How many days a week can I work from home? | [1] Office-based employees may work remotely up to 3 days per week. |
| PASS | answerable | employee | What are the core hours for remote employees? | Remote employees must be available during core hours, 10:00 to 15:00 local time [1]. |
| PASS | answerable | employee | How much is the home office stipend? | The home office stipend is $400. |
| PASS | answerable | employee | What is the minimum password length? | Passwords must be at least 14 characters long [1]. |
| PASS | answerable | employee | I lost my laptop. Who do I call and how quickly? | You should report the lost laptop to the IT Helpdesk on extension 4400 within 2 hours. |
| FAIL | answerable | employee | Which VPN should I use on hotel Wi-Fi? | I couldn't find this in the company documents I have access to. |
| PASS | answerable | employee | When must a shipment delay be escalated to the Operations Manager? | A shipment delay must be escalated to the Operations Manager if it exceeds 24 hours [2]. |
| PASS | answerable | employee | What service credit do contract customers get for a delay over 48 hours? | Contract customers receive a service credit of 5% of the freight charge for that shipment for a delay over 48 hours [1]. |
| PASS | answerable | employee | What does delay code D4 mean? | Delay code D4 is "customs hold" [1]. |
| PASS | answerable | employee | Within how many days must customers report damaged goods? | Customers must report damaged goods within 7 calendar days of delivery [1]. |
| PASS | answerable | employee | Who approves a damage claim worth $300? | According to [1], a claims up to $500 are approved by the Customer Service Lead. |
| PASS | answerable | employee | How often must forklift certification be renewed? | Forklift certification must be renewed every 3 years [1]. |
| PASS | answerable | employee | What is the maximum weight one person may lift manually? | The maximum manual lift for one person is 23 kg [1]. |
| PASS | answerable | employee | How long is the probation period for new employees? | The probation period for new employees is 90 days [1]. |
| PASS | answerable | employee | What format do tracking numbers use? | Tracking numbers start with "HP-" followed by 10 digits, for example HP-4820019377 [1]. |
| PASS | answerable | employee | What is the TrackPort API rate limit? | The TrackPort API rate limit is 600 requests per minute per API key [1]. |
| PASS | answerable | manager | What is the average merit increase budget for 2026? | The average merit increase budget for 2026 is 3.5% of base salary [1]. |
| PASS | answerable | manager | How long does a performance improvement plan last? | A performance improvement plan (PIP) lasts 60 days, with written check-ins every 2 weeks [1]. |
| PASS | answerable | hr | What is the salary band for an Operations Manager? | The salary band for an Operations Manager is $82,000 to $101,000 [1]. |
| PASS | restricted | employee | What is the salary band for a Dispatcher? | I couldn't find this in the company documents I have access to. |
| PASS | restricted | employee | What is the average merit increase budget for 2026? | I couldn't find this in the company documents I have access to. |
| PASS | restricted | manager | What is the salary band for an HR Business Partner? | I couldn't find this in the company documents I have access to. |
| PASS | out_of_scope | employee | What is the company's stock price today? | I couldn't find this in the company documents I have access to. |
| PASS | out_of_scope | employee | Does the company offer a gym membership? | I couldn't find this in the company documents I have access to. |
| PASS | out_of_scope | employee | Who is the CEO of Harbor & Pine Logistics? | I couldn't find this in the company documents I have access to. |
| PASS | out_of_scope | employee | How many days of paternity leave do employees in Germany get under German law? | I couldn't find this in the company documents I have access to. |
