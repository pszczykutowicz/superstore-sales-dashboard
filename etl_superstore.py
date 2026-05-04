import pandas as pd
from sqlalchemy import create_engine, text
import sys

# ------------------------------------------------------------------------------
# Konfiguracja
# ------------------------------------------------------------------------------
DB_USER = "your_username"
DB_PASSWORD = "your_password"
DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_NAME = "superstore_db"
CSV_PATH = r"path\to\superstore_orders.csv"
TABLE_NAME = "orders"
# ------------------------------------------------------------------------------


def load_csv(path):
    """Wczytuje plik CSV, próbując kilku popularnych enkodowań."""
    for encoding in ["utf-8", "latin-1", "windows-1252"]:
        try:
            df = pd.read_csv(path, encoding=encoding)
            print(f"Plik wczytany ({encoding}), liczba wierszy: {len(df)}")
            return df
        except UnicodeDecodeError:
            continue
    print("Nie udalo sie wczytac pliku. Sprawdz enkodowanie.")
    sys.exit(1)


def clean(df):
    """Czyści i typuje dane przed zaladowaniem do bazy."""

    # Kolumna Row ID to zwykly index z CSV, nie potrzebujemy jej w bazie
    if "Row ID" in df.columns:
        df = df.drop(columns=["Row ID"])

    # Ujednolicenie nazw kolumn: male litery, spacje i myslniki na podkreslniki
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
    )

    # Daty sa w formacie DD/MM/YYYY, konwertujemy na typ datetime
    for col in ["order_date", "ship_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors="coerce")
            invalid = df[col].isna().sum()
            if invalid:
                print(
                    f"Ostrzezenie: {col} zawiera {invalid} niepoprawnych dat.")

    # Sales zapisany jako tekst z przecinkiem, konwertujemy na float
    if "sales" in df.columns:
        df["sales"] = (
            df["sales"]
            .astype(str)
            .str.replace(",", ".", regex=False)
            .pipe(pd.to_numeric, errors="coerce")
        )

    # Kod pocztowy zostawiamy jako tekst, zeby nie gubic zer wiodacych
    if "postal_code" in df.columns:
        df["postal_code"] = df["postal_code"].astype(str).str.strip()

    # Usuwamy wiersze, ktore sa calkowicie puste
    rows_before = len(df)
    df = df.dropna(how="all")
    removed = rows_before - len(df)
    if removed:
        print(f"Usunieto {removed} pustych wierszy.")

    print(f"Czyszczenie zakonczone. Kolumny: {list(df.columns)}")
    return df


def load_to_db(df, engine):
    """Laduje DataFrame do tabeli w bazie danych."""
    df.to_sql(
        name=TABLE_NAME,
        con=engine,
        if_exists="replace",
        index=False,
        chunksize=500,
        method="multi",
    )
    print(f"Zaladowano {len(df)} wierszy do tabeli '{TABLE_NAME}'.")


def main():
    df = load_csv(CSV_PATH)
    df = clean(df)

    connection_string = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    try:
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"Polaczono z baza: {DB_NAME}")
    except Exception as error:
        print(f"Blad polaczenia z baza: {error}")
        sys.exit(1)

    try:
        load_to_db(df, engine)
    except Exception as error:
        print(f"Blad ladowania danych: {error}")
        sys.exit(1)

    print("Gotowe.")


if __name__ == "__main__":
    main()
