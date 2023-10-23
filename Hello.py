

import streamlit as st
from streamlit.logger import get_logger
import pandas as pd
import re
LOGGER = get_logger(__name__)


def run():
    st.set_page_config(
        page_title="Stripe Transaction Coding",
        page_icon="👋",
    )

    ledger_file = st.file_uploader("Please upload ledger file in csv")
    stripe_transaction_file = st.file_uploader("Please upload Stripe Treasury file in csv")
    gold_tsy_file = st.file_uploader("Please upload Gold Treasury File")
    platinum_tsy_file = st.file_uploader("Please upload Platinum Treasury file")
    if ledger_file: 
      ledger_df = pd.read_csv(ledger_file)
      st.session_state['tsy'] = False
      if stripe_transaction_file:
        st.session_state['tsy'] = False
        stripe_tsy_df = pd.read_csv(stripe_transaction_file)
        stripe_tsy_df['Amount'] = stripe_tsy_df['Amount'].replace('[\$,]', '', regex=True).astype(float)
        
        
        def code_tsy_transaction(row):
          counterparty = row['Counterparty'].lower()
          category = row['Category'].lower()
          description = row['Description'].lower()
          advance_amount = row["Amount"]
          account = None
          epp = None
          customer = None
          sub_customer = None
          ledger_row = pd.Series() 
          if 'constrafor' in counterparty:
              if 'gold' in counterparty:
                  if 'outbound' in category:
                      account= "Transfer to Gold Tsy"
                  else:
                      account= "Transfer from Gold Tsy"
              elif 'platinum' in counterparty:
                  if '8920' in counterparty:
                      if 'outbound' in category:
                          account= "Transfer to Chase Platinum 8920"
                      else:
                          account= "Transfer from Chase Platinum 8920"
                  elif 'outbound' in category:
                      account = "Transfer to Platinum Tsy"
                  else:
                      account = "Transfer from Platinum Tsy"
              elif 'outbound' in category and 'epp' not in description:
                  account = 'Transfer to Chase 7258'
              elif 'inbound' in category and 'epp' not in description:
                  account = "Transfer from Chase 7258"
          # map epp
          if 'epp' in description and not account:
              #find four digit epp number
              epp_numbers = re.findall(r'\d+', description)
              if len(epp_numbers) > 0:
                  epp_id = int(epp_numbers[0])
                  ledger_row = ledger_df[ledger_df['id'] == epp_id]              
          if not account and not len(ledger_row):
              ledger_row = ledger_df[ledger_df['advance_amount']== abs(advance_amount)]
              
              if not len(ledger_row):
                  ledger_row = ledger_df[ledger_df['purchase_price']== abs(advance_amount)]
              
          if len(ledger_row):
              spv_fund = ledger_row['spv_fund'].values[0]
              epp = ledger_row['id'].values[0]
              customer = ledger_row['subcontractor'].values[0]
              sub_customer = ledger_row['debtor'].values[0]
              if 'gold' in spv_fund.lower():
                  account = "Factor AR - Gold"
              else:
                  account = "Factor AR - Platinum"
          if not account and not len(ledger_row):
              ledger_row = ledger_df[ledger_df['overdue_fee']== abs(advance_amount)]
              if len(ledger_row):
                  epp = ledger_row['id'].values[0]
                  customer = ledger_row['subcontractor'].values[0]
                  account = "Late Fee Income"
          return pd.Series({'Account': account, 'EPP': epp, 'Customer': customer, 'Sub_Customer': sub_customer})
        
        
        columns = stripe_tsy_df.apply(code_tsy_transaction, axis=1)
        all_df = stripe_tsy_df.join(columns)
        if len(all_df)>0:
            all_df.to_csv("stripe_tsy.csv", index=False)   
            st.session_state['tsy'] = True

      if gold_tsy_file:
        st.session_state['gold_tsy'] = False
        gold_tsy_df = pd.read_csv(gold_tsy_file)
        gold_tsy_df['Amount'] = gold_tsy_df['Amount'].replace('[\$,]', '', regex=True).astype(float)
        
        def code_gold_tsy(row):
          counterparty = row['Counterparty'].lower()
          category = row['Category'].lower()
          description = row['Description'].lower()
          advance_amount = row["Amount"]
          account = None
          epp = None
          customer = None
          sub_customer = None
          ledger_row = pd.Series() 
          #print(counterparty)
          #print(category)
          if 'constrafor' in counterparty:
              if 'gold' in counterparty:
                  if 'outbound' in category:
                      account= "Transfer to FRB"
                  else:
                      account= "Transfer from FRB"
              elif 'platinum' in counterparty:
                  if 'outbound' in category:
                      account= "Transfer to Chase 8920"
                  else:
                      account= "Transfer from Chase 8920"
              elif 'outbound' in category:
                  account = "Transfer to Stripe Tsy"
              else:
                  account = "Transfer from Stripe Tsy"
          
          # mapp epp
          #print(description)
          elif 'epp' in description:
              #find four digit epp number
              epp_numbers = re.findall(r'\d+', description)
              print(epp_numbers)
              if len(epp_numbers) > 0:
                  epp_id = int(epp_numbers[0])
                  ledger_row = ledger_df[ledger_df['id'] == epp_id]              
          if not account and not len(ledger_row):
              ledger_row = ledger_df[ledger_df['advance_amount']== abs(advance_amount)]
              
              if not len(ledger_row):
                  ledger_row = ledger_df[ledger_df['purchase_price']== abs(advance_amount)]
              
          if len(ledger_row):
              
              epp = ledger_row['id'].values[0]
              customer = ledger_row['subcontractor'].values[0]
              sub_customer = ledger_row['debtor'].values[0]
              
              account = "Factor AR - Gold"
          return pd.Series({'Account': account, 'EPP': epp, 'Customer_auto': customer, 'Sub_Customer_auto': sub_customer})
        new_columns = gold_tsy_df.apply(code_gold_tsy, axis=1)
        all_gold_df = gold_tsy_df.join(new_columns)
        if len(all_gold_df)>0:
            all_gold_df.to_csv("gold_tsy.csv", index=False)   
            st.session_state['gold'] = True 
      
      if platinum_tsy_file:
        platinum_tsy_df = pd.read_csv(platinum_tsy_file)
        platinum_tsy_df['Amount'] = platinum_tsy_df['Amount'].replace('[\$,]', '', regex=True).astype(float)
        def code_platinum_tsy(row):
          counterparty = row['Counterparty'].lower()
          category = row['Category'].lower()
          description = row['Description'].lower()
          advance_amount = row["Amount"]
          account = None
          epp = None
          customer = None
          sub_customer = None
          ledger_row = pd.Series() 
          #print(counterparty)
          #print(category)
          if 'constrafor' in counterparty:
              if 'gold' in counterparty:
                  if 'outbound' in category:
                      account= "Transfer to FRB"
                  else:
                      account= "Transfer from FRB"
              elif 'platinum' in counterparty:
                  if 'outbound' in category:
                      account= "Transfer to Chase 8920"
                  else:
                      account= "Transfer from Chase 8920"
              elif 'outbound' in category:
                  account = "Transfer to Stripe Tsy"
              else:
                  account = "Transfer from Stripe Tsy"
    
          # mapp epp
          #print(description)
          elif 'epp' in description:
              #find four digit epp number
              epp_numbers = re.findall(r'\d+', description)
              print(epp_numbers)
              if len(epp_numbers) > 0:
                  epp_id = int(epp_numbers[0])
                  ledger_row = ledger_df[ledger_df['id'] == epp_id]              
          if not account and not len(ledger_row):
              ledger_row = ledger_df[ledger_df['advance_amount']== abs(advance_amount)]
              
              if not len(ledger_row):
                  ledger_row = ledger_df[ledger_df['purchase_price']== abs(advance_amount)]
              
          if len(ledger_row):
              
              epp = ledger_row['id'].values[0]
              customer = ledger_row['subcontractor'].values[0]
              sub_customer = ledger_row['debtor'].values[0]
              
              account = "Factor AR - Platinum"
          return pd.Series({'Account_auto': account, 'EPP_auto': epp, 'Customer_auto': customer, 'Sub_Customer_auto': sub_customer})
        
        
        new_platinum = platinum_tsy_df.apply(code_platinum_tsy, axis=1)
        all_platinum_df = platinum_tsy_df.join(new_platinum)
        if len(all_platinum_df)>0:
            all_platinum_df.to_csv("platinum_tsy.csv", index=False)   
            st.session_state['platinum'] = True 


    if st.session_state.get("tsy"):
      with open("stripe_tsy.csv", "rb") as fp:
        btn = st.download_button(
        label="Download Stripe Treasury file",
        data=fp,
        file_name="stripe_tsy.csv",
        mime="text/csv")
    if st.session_state.get("gold"):
        with open("gold_tsy.csv", "rb") as fp:
          st.download_button(
          label="Download Gold Treasury file",
          data=fp,
          file_name="gold_tsy.csv",
          mime="text/csv")
    if st.session_state.get("platinum"):
        with open("platinum_tsy.csv", "rb") as fp:
          st.download_button(
          label="Download Platinum Treasury file",
          data=fp,
          file_name="platinum_tsy.csv",
          mime="text/csv")
if __name__ == "__main__":
    run()
