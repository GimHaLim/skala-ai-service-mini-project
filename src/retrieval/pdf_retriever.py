"""
PDF 문서 검색 관련 기능
"""

import logging
import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_opentutorial.rag.pdf import PDFRetrievalChain

logger = logging.getLogger(__name__)

def setup_pdf_retrieval(pdf_path=None):
    """
    PDF 문서를 로드하고 검색 가능한 벡터 저장소를 생성합니다.
    
    Args:
        pdf_path (str, optional): PDF 파일 경로. 기본값은 None이며, 
                                 이 경우 기본 경로를 사용합니다.
    
    Returns:
        tuple: (retriever, chain, vectorstore) 튜플
    """
    # 기본 PDF 파일 경로
    if pdf_path is None:
        # 프로젝트 루트 디렉토리 기준 상대 경로
        pdf_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "data",
            "Research_on_AI_Ethics_Guidelines.pdf"
        )
    
    logger.info(f"PDF 파일 로드 중: {pdf_path}")
    
    try:
        # PDF 로드
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        logger.info(f"문서의 페이지수: {len(docs)}")

        # 청크 분할
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        split_documents = text_splitter.split_documents(docs)
        logger.info(f"분할된 청크의수: {len(split_documents)}")

        # 임베딩 및 벡터 저장소 생성
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        vectorstore = FAISS.from_documents(documents=split_documents, embedding=embeddings)

        # PDF 검색 체인 생성
        pdf_file = PDFRetrievalChain([pdf_path]).create_chain()

        return pdf_file.retriever, pdf_file.chain, vectorstore
    
    except Exception as e:
        logger.error(f"PDF 처리 중 오류 발생: {str(e)}")
        raise