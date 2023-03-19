import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import plotly.express as px

st.title("Stock Data Analysis")


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
        # st.write(window.values)
        # st.write(similarity_scores)
        return similarity_scores[0]

    # compute the similarity between the last 7 days and each 7-day window in the dataset
    similarity_scores = rolling_window.apply(compute_similarity, raw=False)
    similarity_scores = similarity_scores.fillna(value=0)
    # st.write(similarity_scores)
    # sort the similarity scores in descending order
    top_similarities = similarity_scores.argsort()[-10:]
    # st.write(top_similarities)
    # st.write(similarity_scores[top_similarities])

    # st.write(df["Close"].iloc[953])

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

    st.write("Top 5 most similar patterns:")
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

        df3 = df["Close"].iloc[index : index + 21]

        if len(df3) == 21:

            st.markdown("---")
            st.write("**Case " + str(i) + "**")
            adjusted = st.checkbox("Scale result?", key=index)

            if adjusted:
                df3 = df3 * (df["Close"].iloc[-14:][0] / df3[0])

            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("**Last 14 days**")
                st.write(df1)
            with col2:
                st.write("**Similar case from the past**")
                st.write(df3)
            with col3:
                # Plot the datasets
                st.write("**Plot**")
                plot_dataframes(df1_14, df3)
                st.write("Similarity score")
                st.write(similarity_scores.iloc[index + 13])
            i += 1
