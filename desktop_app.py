# desktop_pdf_chatbot.py
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit,
    QLineEdit, QFileDialog, QLabel, QScrollArea, QHBoxLayout
)
from PyQt6.QtCore import Qt
from main import create_or_load_vectorstore, get_qa_chain

class PDFChatApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📄 PDF Chatbot Desktop")
        self.setGeometry(100, 100, 700, 600)
        self.vectorstore = None
        self.qa_chain = None

        # Main layout
        layout = QVBoxLayout()

        # Upload button
        self.upload_button = QPushButton("📂 Upload PDF")
        self.upload_button.clicked.connect(self.upload_pdf)
        layout.addWidget(self.upload_button)

        # Status label
        self.status_label = QLabel("👆 Upload a PDF to start.")
        layout.addWidget(self.status_label)

        # Chat display
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        layout.addWidget(self.chat_area)

        # Query input
        query_layout = QHBoxLayout()
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("💬 Ask something about the PDF")
        self.query_input.returnPressed.connect(self.ask_question)
        query_layout.addWidget(self.query_input)

        self.clear_button = QPushButton("🧹 Clear Chat")
        self.clear_button.clicked.connect(self.clear_chat)
        query_layout.addWidget(self.clear_button)

        layout.addLayout(query_layout)

        self.setLayout(layout)

    def upload_pdf(self):
        file_dialog = QFileDialog()
        pdf_path, _ = file_dialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if pdf_path:
            self.status_label.setText(f"🔍 Processing PDF: {pdf_path}")
            QApplication.processEvents()  # Update UI while processing
            try:
                self.vectorstore = create_or_load_vectorstore(pdf_path, index_path=f"faiss_index")
                self.qa_chain = get_qa_chain(self.vectorstore)
                self.status_label.setText(f"✅ PDF processed. You can now ask questions.")
            except Exception as e:
                self.status_label.setText(f"⚠️ Error processing PDF: {str(e)}")

    def ask_question(self):
        if not self.qa_chain:
            self.status_label.setText("⚠️ Upload a PDF first!")
            return

        query = self.query_input.text().strip()
        if query:
            self.chat_area.append(f"<b>💬 You:</b> {query}")
            QApplication.processEvents()
            try:
                response = self.qa_chain.invoke({"query": query})
                answer = response.get("result", "⚠️ No answer returned.")
                self.chat_area.append(f"<b>🧠 Bot:</b> {answer}")

                # Show sources if available
                if "source_documents" in response and response["source_documents"]:
                    self.chat_area.append("<i>📑 Sources:</i>")
                    for doc in response["source_documents"]:
                        src = doc.metadata.get("source", "Unknown")
                        self.chat_area.append(f"- {src}")

                self.chat_area.append("")  # Add spacing
            except Exception as e:
                self.chat_area.append(f"⚠️ Error generating answer: {str(e)}")

            self.query_input.clear()
            self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())

    def clear_chat(self):
        self.chat_area.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFChatApp()
    window.show()
    sys.exit(app.exec())
