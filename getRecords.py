from BlockchainConfig import get_total_records, get_signature_result

if __name__ == "__main__":
    total = get_total_records()
    print(f"Total records: {total}")
    for i in range(total):
        rec = get_signature_result(i)
        print(rec)
