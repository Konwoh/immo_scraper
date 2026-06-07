from sklearn.preprocessing import OneHotEncoder
import pandas as pd

class FeatureEngineering:
    def one_hot_encoding(self, df: pd.DataFrame) -> pd.DataFrame:
        categorical_cols = df.select_dtypes(include=['object']).columns
        encoder = OneHotEncoder(sparse_output=False, min_frequency=20, handle_unknown='infrequent_if_exist')
        
        encoded_data = encoder.fit_transform(df[categorical_cols])
        
        encoded_df = pd.DataFrame(encoded_data, columns=encoder.get_feature_names_out(categorical_cols), index=df.index)
        
        final_df = pd.concat([df.drop(columns=categorical_cols), encoded_df],axis=1)
        
        return final_df