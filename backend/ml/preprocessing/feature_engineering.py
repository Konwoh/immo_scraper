from sklearn.preprocessing import OneHotEncoder, StandardScaler
import pandas as pd
from typing import List, cast
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from stop_words import get_stop_words

class FeatureEngineering:
    
    def _remove_nan(self, df, drop_rows: bool = True):
        nan_cols = [col for col in df.columns if "_nan" in col]
        if drop_rows:
            for col in nan_cols:
                df.drop(df[df[col] == 1].index, inplace=True)
        df.drop(columns=nan_cols, inplace=True, errors="ignore")
        return df


    def one_hot_encoding(self, df: pd.DataFrame, min_frequency: int | None = 5, drop_nan_rows: bool = True) -> pd.DataFrame:
        categorical_cols = df.select_dtypes(include=['object']).columns
        encoder = OneHotEncoder(sparse_output=False, min_frequency=min_frequency, handle_unknown='infrequent_if_exist')

        encoded_data = encoder.fit_transform(df[categorical_cols])

        encoded_df = pd.DataFrame(encoded_data, columns=encoder.get_feature_names_out(categorical_cols), index=df.index)

        df = pd.concat([df.drop(columns=categorical_cols), encoded_df],axis=1)

        final_df = self._remove_nan(df, drop_rows=drop_nan_rows)

        return final_df

    def standardization(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        cols = [col for col in columns if col in df.columns]
        df_standardized = df.copy()
        df_standardized[cols] = np.log1p(df_standardized[cols])
        df_standardized[cols] = StandardScaler().fit_transform(df_standardized[cols])
        return df_standardized

    def text_tokenization(self, df: pd.DataFrame, columns: List[str], max_features: int | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
        blob = df[columns].fillna("").agg(" ".join, axis=1)

        stop_words = get_stop_words("german")
        tfidf = TfidfVectorizer(stop_words=stop_words, max_features=max_features)
        tfidf_matrix = cast(csr_matrix, tfidf.fit_transform(blob))

        tfidf_df = pd.DataFrame(
            tfidf_matrix.toarray(),
            index=df.index,
            columns=tfidf.get_feature_names_out(),
        )

        return df.drop(columns=columns), tfidf_df