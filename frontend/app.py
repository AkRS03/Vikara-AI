import streamlit as st
import requests

BACKEND = "https://vikara-ai.onrender.com"  # deployed backend URL

st.title("Support Ticket System (Prototype)")


if "ticket_id" not in st.session_state:
    st.session_state.ticket_id = None

username = st.text_input("Your Name")
question = st.text_area("Describe your issue")

# Submit Ticket
submit_disabled = not username or not question
if st.button("Submit Ticket", disabled=submit_disabled):
    try:
        r = requests.post(
            f"{BACKEND}/tickets/create",
            json={"username": username, "question": question},
            timeout=10
        )
        r.raise_for_status()
        data = r.json()

        st.session_state.ticket_id = data.get("ticket_id")
        st.success(f"Ticket ID: {st.session_state.ticket_id}")
        st.write("### LLM Answer:")
        st.write(data.get("response", "No response received."))

    except requests.RequestException as e:
        st.error(f"Failed to submit ticket: {e}")


if st.session_state.ticket_id:
    st.write("---")
    st.write("Was your issue resolved?")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Yes, resolved"):
            try:
                r = requests.post(
                    f"{BACKEND}/tickets/resolve",
                    json={"ticket_id": st.session_state.ticket_id, "resolved": True},
                    timeout=10
                )
                r.raise_for_status()
                st.success("Glad it's resolved! Ticket closed.")
                st.session_state.ticket_id = None  # reset

            except requests.RequestException as e:
                st.error(f"Failed to update ticket: {e}")

    with c2:
        if st.button("No, not resolved"):
            try:
                r = requests.post(
                    f"{BACKEND}/tickets/resolve",
                    json={"ticket_id": st.session_state.ticket_id, "resolved": False},
                    timeout=10
                )
                r.raise_for_status()
                info = r.json()
                st.error("Please contact support:")
                st.write(f"Agent: {info.get('agent_name', 'N/A')}")
                st.write(f"Phone: {info.get('phone', 'N/A')}")

            except requests.RequestException as e:
                st.error(f"Failed to update ticket: {e}")
