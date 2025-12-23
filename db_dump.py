import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def create_dump():
    """Create PostgreSQL database dump using Docker container."""
    db = os.getenv("POSTGRES_DB", "autoria")
    user = os.getenv("POSTGRES_USER", "postgres")
    dumps_dir = os.getenv("DUMPS_DIR", "dumps")
    container_name = "autoria_db"

    # Create dumps directory if not exists
    os.makedirs(dumps_dir, exist_ok=True)

    # Generate dump filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dump_file = os.path.join(dumps_dir, f"autoria_dump_{timestamp}.sql")

    # Run pg_dump via docker exec
    cmd = [
        "docker", "exec", container_name,
        "pg_dump", "-U", user, "-d", db
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Write dump to file
        with open(dump_file, "w") as f:
            f.write(result.stdout)

        print(f"Database dump created: {dump_file}")
        return dump_file
    except subprocess.CalledProcessError as e:
        print(f"Error creating dump: {e.stderr}")
        return None
    except FileNotFoundError:
        print("Docker not found. Make sure Docker is installed and running.")
        return None


if __name__ == "__main__":
    create_dump()
