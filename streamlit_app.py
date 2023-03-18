import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import plotly.express as px

st.title("Stock Data Analysis")

n_window = 14

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
    df = pd.read_csv(uploaded_file)
    df = df.set_index("Date")
    # create a rolling window of 7 days
    df = df[-years * 365 :]
    rolling_window = df["Close"].rolling(window=n_window)

    # define a function to compute the similarity between the last 7 days and each 7-day window in the dataset
    def compute_similarity(window):
        last_seven_days = df["Close"].iloc[-n_window:]
        similarity_scores = cosine_similarity(
            last_seven_days.values.reshape(1, -1), window.values.reshape(1, -1)
        )
        return similarity_scores[0]

    # compute the similarity between the last 7 days and each 7-day window in the dataset
    similarity_scores = rolling_window.apply(compute_similarity, raw=False)
    # sort the similarity scores in descending order
    top_five_similarities = np.argsort(similarity_scores)[-10:]
    # st.write(top_five_similarities)
    # st.write(similarity_scores)
    # plot the projected closing data for each of the 5 most similar patterns

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
    for index in top_five_similarities:
        # plot the last 14 days
        # create a series with 7 null values
        null_series = pd.Series([None] * 7)

        # concatenate the original series and the null series

        df1 = df["Close"].iloc[-14:]

        df1_14 = pd.concat([df1, null_series])

        # df2 = df["Close"].iloc[index : index + 7]
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
                st.write(similarity_scores[index])
            i += 1
