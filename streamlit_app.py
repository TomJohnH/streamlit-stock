import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import plotly.express as px

st.title("Stock Data Analysis")


######
#
#   This will be replaced by conection to the database
#
######

example = """<ul> <li>2008-08-28: Fed approves $200 billion emergency loan program for banks</li> <li>2008-08-29: Fannie Mae and Freddie Mac shares plunge amid bailout fears</li> <li>2008-09-02: Lehman Brothers reports $3.9 billion loss, plans to sell assets</li> <li>2008-09-07: US government takes over Fannie Mae and Freddie Mac</li> <li>2008-09-08: Bank of America agrees to buy Merrill Lynch for $50 billion</li> <li>2008-09-15: Lehman Brothers files for bankruptcy, AIG seeks federal aid</li> <li>2008-09-16: Fed bails out AIG with $85 billion loan, Barclays buys Lehman’s US assets</li> <li>2008-09-17: Fed lends $180 billion to foreign central banks, SEC bans short-selling of financial stocks</li> <li>2008-09-18: Treasury proposes $700 billion bailout plan for financial firms</li> <li>2008-09-19: Fed and other central banks inject $180 billion into money markets, US stocks rally</li> <li>2008-09-21: Goldman Sachs and Morgan Stanley become bank holding companies</li> <li>2008-09-23: Fed lends $30 billion to JPMorgan Chase to buy Bear Stearns’ assets</li> <li>2008-09-25: Washington Mutual seized by regulators, sold to JPMorgan Chase</li>"""


# allow user to upload a CSV file containing stock data
uploaded_file = st.file_uploader(
    "Upload stock quotes *.csv",
    type=["csv"],
    help="The file has to have at least a Date column and a Close column. Stock quotes should be sorted from oldest to newest. ",
)

if st.checkbox("Use example file"):
    uploaded_file = "pko_d.csv"

years = st.slider("How many years of data take into account?", 1, 20, 20)


if uploaded_file is not None:
    n_window = 14
    df = pd.read_csv(uploaded_file)
    headlines = pd.read_csv("headlines.csv")
    headlines_m = pd.read_csv("headlines_m.csv")
    df = df.set_index("Date")
    # create a rolling window of 14 days
    df = df[-years * 365 :]
    rolling_window = df["Close"].rolling(window=n_window)

    # dfa = [window.to_list() for window in rolling_window]
    # st.write(dfa)

    # define a function to compute the similarity between the last 14 days and each 14-day window in the dataset
    def compute_similarity(window):
        last_n_days = df["Close"].iloc[-n_window:]
        similarity_scores = cosine_similarity(
            last_n_days.values.reshape(1, -1), window.values.reshape(1, -1)
        )
        return similarity_scores[0]

    # compute the similarity between the last 7 days and each 7-day window in the dataset
    similarity_scores = rolling_window.apply(compute_similarity, raw=False)
    similarity_scores = similarity_scores.fillna(value=0)
    top_similarities = similarity_scores.argsort()[-10:]

    def plot_dataframes(df1, df2):
        # Create the plots
        fig, ax = plt.subplots()
        ax.plot(range(1, 22), df1, label="Last 14 days")
        ax.plot(range(1, 22), df2, label="Similar case from the past")

        # Set the chart title and legend
        ax.set_title("Two Plots on One Chart")
        ax.legend()

        # Display the chart using Streamlit
        st.pyplot(fig)

    st.write("Top most similar patterns:")
    i = 1
    for index in top_similarities:
        # plot the last 14 days
        # create a series with 7 null values
        null_series = pd.Series([None] * 7)

        # has to be done in order to provide correct window
        index = index - (n_window - 1)

        # concatenate the original series and the null series

        df1 = df["Close"].iloc[-14:]

        df1_14 = pd.concat([df1, null_series])

        df_past = df["Close"].iloc[index : index + 21]

        if len(df_past) == 21:

            st.markdown("---")
            st.write("**Case " + str(i) + "**")
            adjusted = st.checkbox("Scale result?", key=index)

            if adjusted:
                df_past = df_past * (df["Close"].iloc[-14:][0] / df_past[0])

            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("**Last 14 days**")
                st.write(df1)
            with col2:
                st.write("**Similar case from the past**")
                st.write(df_past)
            with col3:
                # Plot the datasets
                st.write("**Plot**")
                plot_dataframes(df1_14, df_past)
                st.write("Similarity score")
                st.write(similarity_scores.iloc[index + 13])
            st.write(
                "**Financial market headlines published from "
                + str(df.iloc[index].name)
                + "**"
            )
            if headlines["Date"].eq(df.iloc[index].name).any():

                html = str(
                    headlines[headlines["Date"] == df.iloc[index].name][
                        "Headlines"
                    ].values[0]
                )
                # st.write(html)
                st.markdown(
                    html,
                    unsafe_allow_html=True,
                )

            else:
                if headlines_m["Date"].eq(df.iloc[index].name[0:7]).any():
                    html = str(
                        headlines_m[headlines_m["Date"] == df.iloc[index].name[0:7]][
                            "Headlines"
                        ].values[0]
                    )
                    st.markdown(
                        html,
                        unsafe_allow_html=True,
                    )
                else:
                    st.write("No data")
            i += 1

# Could you provide me with financial market headlines published on 2008-09-16. Present them in html code. Do not add references in list.
