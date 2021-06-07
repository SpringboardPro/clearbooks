#%%
from io import StringIO
import pandas as pd
from clearbooks import Session, TIMEOUT

#%%
REPORT_URL = 'https://secure.clearbooks.co.uk/springboardproltd/accounting/reports/export-csv/'

params = {
    'report_type': 'POS',
    'q_from': '03/05/2021',
    'q_to': '07/06/2021',
}

#%%
with Session() as session:
    response = session._session.post(REPORT_URL, params, timeout=TIMEOUT)

response.raise_for_status()

# print(response.text)

#%%
df = pd.read_csv(StringIO(response.text), parse_dates=[2, 4])
df
#%%
