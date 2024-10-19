import streamlit as st
import requests
import jwt
import logging
import time
# from jose import jwt
from dotenv import load_dotenv
import os

logging.basicConfig(level=logging.INFO)

api_url = "http://app:8080"

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")


def create_access_token(user: str) -> str:
    payload = {
        "user": user,
        "expires": time.time() + 3600
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


def authenticate(username, password):
    response = requests.post(f"{api_url}/user/signin",
                             data={"username": username, "password": password})
    if response.status_code == 200:
        json_response = response.json()
        logging.info(f"JSON response: {json_response}")
        token = response.json().get("access_token")
        user_id = response.json().get("user_id")
        return token, user_id
    else:
        return None


def verify_access_token(token):
    try:
        jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return True
    except jwt.ExpiredSignatureError:
        logging.error("Token has expired")
    except jwt.InvalidTokenError as e:
        logging.error(f"Invalid token: {e}")


def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state['redirect_to'] = "Главная"
    st.rerun()


def main_page():
    st.title("Добро пожаловать в наш сервис «Кикстартерный Нострадамус» 🔮")
    st.write(f"система прогнозирования 📈📉"
             f"успеха стартапов на платформе Kickstarter 🎰 "
             f"с использованием машинного обучения 💻")
    st.header("Аутентификация ☑️")
    username = st.text_input("Логин", key="user_login")
    password = st.text_input("Пароль", type="password", key="user_password")
    if st.button("Войти", key="registered_user"):
        token, user_id = authenticate(username, password)
        if token:
            st.success("Успешная аутентификация!")
            st.session_state['token'] = token
            st.session_state['user_id'] = user_id
            st.session_state['username'] = username
            st.session_state['logged_in'] = True
            st.write(
                f"User после аутентификации: {st.session_state.get('username')}")
            st.session_state['redirect_to'] = "Личный кабинет"
            st.rerun()
        else:
            st.error("Ошибка аутентификации")

        st.session_state['redirect_to'] = "Личный кабинет"
        st.rerun()

    if st.button("Перейти к регистрации"):
        st.session_state['redirect_to'] = "Регистрация"
        st.rerun()


def registration_page():
    st.title("Регистрация 📝")
    st.write(f" При регистрации 100 кредитов в подарок  🎁")
    username = st.text_input("Логин", key="new_user_login")
    st.session_state['Логин'] = username
    email = st.text_input("Email", key="new_user_email")
    st.session_state['Email'] = email
    password = st.text_input("Пароль", type="password",
                             key="new_user_password")
    st.session_state['Пароль'] = password
    if st.button("Зарегистрироваться"):
        response = requests.post(f"{api_url}/user/signup",
                                 json={"username": username,
                                       "email": email,
                                       "password": password})
        if response.status_code == 200:
            st.success(
                "Регистрация выполнена успешно. Перенаправление на страницу входа...")
            if username:
                token, user_id = authenticate(username, password)
                st.session_state['token'] = token
                st.session_state['user_id'] = user_id
                st.session_state['username'] = username
                st.write(
                    f"User после регистрации: {st.session_state.get('username')}")
                st.session_state['user_id'] = user_id
                st.session_state['username'] = username
                st.session_state['logged_in'] = True
                st.session_state['redirect_to'] = "Личный кабинет"
                st.rerun()
            else:
                st.error(
                    "Ошибка при получении username из ответа на регистрацию")
            # st.session_state['redirect_to'] = "Главная"
            # st.rerun()

def user_dashboard():
    st.title("Личный кабинет")
    if 'token' not in st.session_state or 'username' not in st.session_state:
        st.error(
            "Пожалуйста, войдите в систему для доступа к личному кабинету")
        st.stop()
    token = st.session_state['token']
    user_id = st.session_state['user_id']
    if not verify_access_token(token):
        st.error("Недействительный токен доступа. Пожалуйста, войдите заново.")
        st.stop()

    username = st.session_state.get('username', 'Unknown')

    st.header(f"Пользователь: {username} - ✅")

    st.header(f"Баланс 💲")
    response_username = requests.get(f"{api_url}/user/user",
                                     params={"username": username})
    if response_username.status_code == 200:
        user_data = response_username.json()
        user_id = user_data.get('id')

    response = requests.get(f"{api_url}/user/balance/{user_id}")

    if response.status_code == 200:
        balance = response.json().get('balance', 'N/A')
        st.write(f"Сумма кредитом: {balance}")
    else:
        st.write("Ошибка при получении информации о балансе")

    st.header("Пополнение баланса 💳")
    user_id = st.session_state['user_id']
    amount = st.number_input("Сумма пополнения", min_value=0, key="summa_add")
    if st.button("Пополнить баланс"):
        response = requests.post(f"{api_url}/user/balance/add/{user_id}",
                                 params={"amount": amount})
        if response.status_code == 200:
            logging.info(f"Баланс успешно пополнен!")
            st.success("Баланс успешно пополнен!")
            st.rerun()
        else:
            st.error("Ошибка пополнения баланса")

    st.header("История транзакций 🔍")
    user_id = st.session_state['user_id']
    response = requests.get(
        f"{api_url}/transaction/transactions_history/{user_id}")
    if response.status_code == 200:
        transaction_history = response.json()
        st.write(transaction_history)


def ml_service_page():
    st.title("ML Сервис")
    st.write(f"Стоимость предсказания:  50 кредитов 💸")
    if 'token' not in st.session_state or 'user_id' not in st.session_state:
        st.error("Пожалуйста, войдите в систему для доступа к ML сервису")
        st.stop()

    token = st.session_state['token']
    if not verify_access_token(token):
        st.error("Недействительный токен доступа. Пожалуйста, войдите заново.")
        st.stop()

    user_id = st.session_state['user_id']

    st.header("Выбор модели")
    models = ["MLModel"]
    selected_model = st.selectbox("Выберите модель", models)
    st.write(f"Вы выбрали: {selected_model}")

    if st.button("Загрузить модель"):
        response = requests.post(f"{api_url}/model/upload_model",
                                 json={"model_name": "MLModel",
                                       "description": "LogisticRegression"})
        if response.status_code == 200:
            json_response = response.json()
            model_id = json_response.get('model_id', 'N/A')
            st.session_state['model_id'] = model_id
            st.success("Модель успешно загружена!")
        else:
            st.error("Ошибка загрузки модели")

    if 'model_id' not in st.session_state:
        st.error("Сначала загрузите модель")
        return

    model_id = st.session_state['model_id']

    st.header("Kickstarter Nostradamus")

    blurb = st.text_input('Описание', 'Chill Magazine is a woman run, print-only literary art magazine for chillers. We need help bringing our third issue to life!')
    currency = st.text_input('Валюта', 'USD')
    goal = st.number_input('Цель', 3500)
    campaign_duration = st.number_input('Продолжительность', 30)
    started_month = st.number_input('Месяц старта', 7)
    category_subcategory = st.text_input('Категория', 'Publishing Art Books')

    if st.button('Загрузить данные'):
        user_id = st.session_state['user_id']
        model_id = st.session_state['model_id']
        st.session_state['task_id'] = None

        input_data = {
            'blurb': blurb,
            'currency': currency,
            'goal': goal,
            'campaign_duration': campaign_duration,
            'started_month': started_month,
            'category_subcategory': category_subcategory
        }

        url = f"{api_url}/task/newtask"
        params = {
            "user_id": user_id,
            "model_id": model_id,
        }

        try:
            response = requests.post(url, params=params, json=input_data)
            # st.write("Ответ сервера (raw text):", response.text)
            if response.status_code == 200:
                json_response = response.json()
                task_id = json_response.get('task_id', 'N/A')
                st.session_state['task_id'] = task_id
                st.session_state['model_id'] = model_id
                st.success(f"Задание успешно отправлено, task_id: {task_id}, model_id: {model_id}")
            else:
                st.error(f"Ошибка при отправке задания: {response.status_code}")
                st.write(response.text)

        except requests.exceptions.RequestException as e:
            st.error(f"Ошибка соединения с API: {e}")

    if st.button('Predict Success'):
        task_id = st.session_state.get('task_id')
        url = f"{api_url}/task/prediction/{task_id}"

        if task_id:
            response = requests.get(url)
            if response.status_code == 200:
                json_response = response.json()
                output_data = json_response.get('output_data', 'Нет данных')
                st.success(f"Рекомендация: {output_data}")
            else:
                st.error("Ошибка при получении предсказания")
        else:
            st.error("Task ID не найден. Сначала загрузите данные.")

    st.header("История запросов и предсказаний ")
    response = requests.get(f"{api_url}/prediction/{user_id}")
    if response.status_code == 200:
        prediction_history = response.json()
        st.write(prediction_history)


def sidebar_navigation():
    if st.sidebar.button("Главная"):
        st.session_state['redirect_to'] = "Главная"
    if st.sidebar.button("Личный кабинет"):
        st.session_state['redirect_to'] = "Личный кабинет"
    if st.sidebar.button("Сервис"):
        st.session_state['redirect_to'] = "Сервис"
    if st.sidebar.button("Регистрация"):
        st.session_state['redirect_to'] = "Регистрация"
    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        if st.sidebar.button("Выйти"):
            logout()


def main():
    st.sidebar.title("Навигация")
    sidebar_navigation()

    if 'redirect_to' in st.session_state:
        if st.session_state['redirect_to'] == "Личный кабинет":
            user_dashboard()
        elif st.session_state['redirect_to'] == "Регистрация":
            registration_page()
        elif st.session_state['redirect_to'] == "Сервис":
            ml_service_page()
        elif st.session_state['redirect_to'] == "Главная":
            main_page()
    elif 'logged_in' in st.session_state and st.session_state['logged_in']:
        user_dashboard()
    else:
        main_page()

if __name__ == "__main__":
    main()
