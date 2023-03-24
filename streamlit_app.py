import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt

st.title("Yet Another Stock Data Analysis")

# allow user to upload a CSV file containing stock data
uploaded_file = st.file_uploader(
    "Upload stock quotes *.csv",
    type=["csv"],
    help="The file has to have at least a Date column and a Close column. Stock quotes should be sorted from oldest to newest. ",
)

# allow user to play around with the app without uploading the file
if st.checkbox("Use example file"):
    uploaded_file = "gs_us_d.csv"

# allow user to limit analysis period
years = st.slider("How many years of data take into account?", 1, 20, 20)

# welcome note and disclaimers
with st.sidebar:
    st.write("**Welcome note**")
    st.write(
        "Welcome to the stock quote analysis app! The app allows users to easily compare the last 14 days of closing stock quotes to all historical 14 day windows. By doing so, similarity scores are calculated and results are presented in the form of tables and graphs. Additionally, if available, the app presents relevant major events that affected the stock market for the historical period."
    )
    st.write(
        """To rescale the historical data to current levels, please select the 'Scale results' checkbox."""
    )
    st.write("**Disclaimer**")
    st.write(
        "Please note that the information provided by this app is for educational and informational purposes only. It is not intended to be used as a basis for making investment decisions. The results presented by the app are based on historical data and are not indicative of future performance. Users are advised to conduct their own research and seek the advice of a qualified financial advisor before making any investment decisions. The app's creators and developers are not responsible for any losses or damages that may occur as a result of using this app or relying on the information provided by it."
    )
    st.write(
        "News headlines were generated using Bing Chat and were not independently reviewed."
    )

# -------------------------
#
#       MAIN APP CODE
#
# -------------------------

if uploaded_file is not None:

    # ----- data load ----

    # we will analysis 14-day periods
    n_window = 14

    # let's read data stock quotes from the csv
    df = pd.read_csv(uploaded_file)

    if "Data" in df.columns:
        df.rename(columns={"Data": "Date"}, inplace=True)
    if "Zamkniecie" in df.columns:
        df.rename(columns={"Zamkniecie": "Close"}, inplace=True)
    if "Najwyzszy" in df.columns:
        df.rename(columns={"Najwyzszy": "Max"}, inplace=True)
    if "Najnizszy" in df.columns:
        df.rename(columns={"Najnizszy": "Min"}, inplace=True)
    if "Wolumen" in df.columns:
        df.rename(columns={"Wolumen": "Volume"}, inplace=True)

    df = df.set_index("Date")

    # let's read headlines data
    headlines = pd.read_csv("headlines.csv")
    headlines_m = pd.read_csv("headlines_m.csv")

    # ----- data manipulation ----

    # create a rolling window of 14 days
    df = df[-years * 365 :]
    rolling_window = df["Close"].rolling(window=n_window)

    # if i would like to see all rolling windows in the future i can use this part:
    # dfa = [window.to_list() for window in rolling_window]
    # st.write(dfa)

    # define a function to compute the similarity between the last n days and each n-day window in the dataset
    def compute_similarity(window):
        last_n_days = df["Close"].iloc[-n_window:]
        similarity_scores = cosine_similarity(
            last_n_days.values.reshape(1, -1), window.values.reshape(1, -1)
        )
        return similarity_scores[0]

    # compute the similarity between the last n days and each n-day window in the dataset
    similarity_scores = rolling_window.apply(compute_similarity, raw=False)
    similarity_scores = similarity_scores.fillna(value=0)
    top_similarities = similarity_scores.argsort()[-10:]

    # define a function to make plots
    def plot_dataframes(df1, df2):
        # Create the plots
        fig, ax = plt.subplots()
        ax.plot(range(1, 22), df1, label="Last 14 days")
        ax.plot(range(1, 22), df2, label="Similar case from the past")

        # Set the chart title and legend
        ax.set_title("Stock quotes similarity")
        ax.legend()

        # Display the chart using Streamlit
        st.pyplot(fig)

    # ----- calculationsn ----

    i = 1
    df_past_list = []
    df_past_list_last = []
    for index in top_similarities:

        # create a series with 7 null values - this will become usefull in a minute
        null_series = pd.Series([None] * 7)

        # has to be done in order to provide correct window for the tables and plots
        index = index - (n_window - 1)

        # create data frame with n last days
        df1 = df["Close"].iloc[-n_window:]

        # concatenate the original series and the null series
        df1_plus_nulls = pd.concat([df1, null_series])

        # create a data frame for historical window
        df_past = df["Close"].iloc[index : index + 21]

        # create a data frame adjusted for first period
        df_past_adj = df_past * (df["Close"].iloc[-14:][0] / df_past[0])

        # create a data frame adjusted for first period
        df_past_adj_last = df_past * (df["Close"].iloc[-1:][0] / df_past[13])

        # append lists
        df_past_list.append(df_past_adj.values.tolist())
        df_past_list_last.append(df_past_adj_last.values.tolist())

        # take into account only periods that large enough to take a peek into the future
        if len(df_past) == 21:

            # ----- front end ----

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
                plot_dataframes(df1_plus_nulls, df_past)
                st.write("Similarity score")
                st.write(similarity_scores.iloc[index + 13])
            st.write(
                "**Major events that affected the stock market in "
                + str(df.iloc[index].name)[0:7]
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
                    st.write("No data. Chat Bing prompt:")
                    st.write(
                        " *What were the major events that affected the stock market in "
                        + str(df.iloc[index].name[0:7])
                        + "?*"
                    )
            i += 1

    st.markdown("---")
    st.write("**Results summarized on one chart (scaled to first period)**")
    df_past_list = pd.DataFrame(df_past_list)
    # st.write(df_past_list)
    fig, ax = plt.subplots()
    for i in range(0, len(df_past_list)):
        ax.plot(range(1, 22), df_past_list.iloc[i], label="Last 14 days", alpha=0.2)
    ax.plot(range(1, 22), df1_plus_nulls, label="Last 14 days", color="red")
    # Set the chart title and legend
    ax.set_title("Stock quotes similarity")

    # Display the chart using Streamlit
    st.pyplot(fig)

    st.write("**Results summarized on one chart (scaled to last period)**")
    df_past_list_last = pd.DataFrame(df_past_list_last)
    # st.write(df_past_list)
    fig, ax = plt.subplots()
    for i in range(0, len(df_past_list_last)):
        ax.plot(
            range(1, 22), df_past_list_last.iloc[i], label="Last 14 days", alpha=0.2
        )
    ax.plot(range(1, 22), df1_plus_nulls, label="Last 14 days", color="red")
    # Set the chart title and legend
    ax.set_title("Stock quotes similarity")

    # Display the chart using Streamlit
    st.pyplot(fig)

# prompts for chat bot
# What were the major events that affected the stock market in may 2005? Please present them in html code. Do not add references.
