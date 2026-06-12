"""Ad Copy Generator with AIDA Framework. Author: Avatar Putra Sigit"""
import streamlit as st
from templates import generate_aida

def main() -> None:
    """Render the Streamlit ad copy generator UI."""
    st.set_page_config(page_title="Ad Copy Generator", layout="wide")
    st.title("✍️ Ad Copy Generator — AIDA Framework")
    st.markdown("Generate variasi copy iklan untuk jasa B2B Indonesia")

    with st.sidebar:
        st.header("⚙️ Input")
        product = st.text_input("Nama Produk/Brand", "PT RKARI")
        service = st.selectbox("Jenis Layanan", ["rope_access", "glass_cleaning", "maintenance"])
        benefit = st.text_input("Benefit Utama", "Hemat 40% biaya maintenance")
        tone = st.selectbox("Tone", ["profesional", "urgent", "friendly"])
        phone = st.text_input("Kontak", "0812-3456-7890")
        n_variations = st.slider("Jumlah Variasi", 1, 5, 3)

    st.markdown("---")

    for i in range(n_variations):
        copy = generate_aida(product, service, benefit, tone, phone)
        with st.container():
            st.subheader(f"Variasi #{i+1}")
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f"**🔴 Attention**\n\n{copy['attention']}")
            c2.markdown(f"**🟡 Interest**\n\n{copy['interest']}")
            c3.markdown(f"**🟢 Desire**\n\n{copy['desire']}")
            c4.markdown(f"**🔵 Action**\n\n{copy['action']}")
            full_copy = f"{copy['attention']}\n\n{copy['interest']}\n\n{copy['desire']}\n\n{copy['action']}"
            st.text_area("Full Copy", full_copy, height=120, key=f"copy_{i}")
            st.markdown("---")

    st.sidebar.info("💡 Tips: AIDA = Attention → Interest → Desire → Action")

if __name__ == "__main__":
    main()
