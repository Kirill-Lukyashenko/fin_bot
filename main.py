from database import create_tables

def main() -> None:
    create_tables()
    print("База данных успешно создана")

if __name__ == "__main__":
    main()