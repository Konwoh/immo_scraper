from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
import pandas as pd
from typing import List
import numpy as np

class FeatureEngineering:
    
    def _remove_nan(self, df):
        for col in df.columns:
            if "_nan" in col:
                df.drop(df[df[col] == 1].index, inplace=True)
                df.drop(col, axis=1, inplace=True)
        return df
    
    
    def one_hot_encoding(self, df: pd.DataFrame) -> pd.DataFrame:
        categorical_cols = df.select_dtypes(include=['object']).columns
        encoder = OneHotEncoder(sparse_output=False, min_frequency=20, handle_unknown='infrequent_if_exist')
        
        encoded_data = encoder.fit_transform(df[categorical_cols])
        
        encoded_df = pd.DataFrame(encoded_data, columns=encoder.get_feature_names_out(categorical_cols), index=df.index)
        
        df = pd.concat([df.drop(columns=categorical_cols), encoded_df],axis=1)
        
        final_df = self._remove_nan(df)
        
        return final_df

    def standardization(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        df_standardized = df.copy()
        df_standardized[columns] = np.log1p(df_standardized[columns])
        df_standardized[columns] = StandardScaler().fit_transform(df_standardized[columns])
        return df_standardized