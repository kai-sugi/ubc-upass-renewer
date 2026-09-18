import keyring

SERVICE = "ubc-upass-automator"

username = keyring.get_password(SERVICE, "username")
password = keyring.get_password(SERVICE, "password")

print("Username:", username)
print("Password Retrieved:", password is not None)

