import miro_api
import dotenv

dotenv.load_dotenv()

miro = miro_api.Miro()

print(miro.auth_url)
