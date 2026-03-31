import pandas as pd

from src.constants import PROCESSED_DATA_PATH, KEGGLE_DATA_PATH

def     load_data(user,
              target_col,
              df = pd.read_csv(PROCESSED_DATA_PATH),
              total_base = pd.read_csv(KEGGLE_DATA_PATH).drop(columns=['Unnamed: 0', ]),
              ):
    user = user.lower().strip().replace(" ", "_")

    return user, target_col, total_base, df

def prepare_training_data(df, user):
    pass

def train_model(x_train, y_train):
    pass

def evaluate_model(model, x_test, y_test):
    pass

def generate_recommendations(model, df, keggle):
    pass