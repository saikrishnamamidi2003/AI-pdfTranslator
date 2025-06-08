import fitz  # PyMuPDF
from googletrans import Translator
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfutils
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.fonts import addMapping
import logging
import re
import os
import urllib.request
import concurrent.futures
import time

class PDFProcessor:
    def __init__(self):
        self.translator = Translator()
        self.setup_unicode_fonts()
    
    def setup_unicode_fonts(self):
        """Setup Unicode fonts for Hindi, Telugu and other languages"""
        try:
            # Create fonts directory if it doesn't exist
            fonts_dir = "fonts"
            if not os.path.exists(fonts_dir):
                os.makedirs(fonts_dir)
            
            # Only download fonts if they don't exist (caching)
            if not self.fonts_exist(fonts_dir):
                logging.info("Downloading Unicode fonts...")
                self.download_unicode_fonts(fonts_dir)
            
            # Register fonts
            self.register_fonts(fonts_dir)
            
        except Exception as e:
            logging.warning(f"Could not setup Unicode fonts: {e}")
    
    def fonts_exist(self, fonts_dir):
        """Check if required fonts already exist"""
        required_fonts = [
            'NotoSans-Regular.ttf',
            'NotoSansDevanagari-Regular.ttf',
            'NotoSansTelugu-Regular.ttf'
        ]
        
        for font_name in required_fonts:
            font_path = os.path.join(fonts_dir, font_name)
            if not os.path.exists(font_path):
                return False
        return True
    
    def download_unicode_fonts(self, fonts_dir):
        """Download Unicode fonts from Google Fonts"""
        fonts_to_download = [
            {
                'name': 'NotoSans-Regular.ttf',
                'url': 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf'
            },
            {
                'name': 'NotoSansDevanagari-Regular.ttf', 
                'url': 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf'
            },
            {
                'name': 'NotoSerifTelugu-Regular.ttf',
                'url': 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSerifTelugu/NotoSerifTelugu-Regular.ttf'
            },
            {
                'name': 'NotoSansTelugu-Bold.ttf',
                'url': 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansTelugu/NotoSansTelugu-Bold.ttf'
            }
        ]
        
        for font_info in fonts_to_download:
            font_path = os.path.join(fonts_dir, font_info['name'])
            if not os.path.exists(font_path):
                try:
                    logging.info(f"Downloading font: {font_info['name']}")
                    urllib.request.urlretrieve(font_info['url'], font_path)
                except Exception as e:
                    logging.warning(f"Could not download font {font_info['name']}: {e}")
    
    def register_fonts(self, fonts_dir):
        """Register downloaded fonts with ReportLab"""
        try:
            # Register Noto Sans (Latin)
            noto_sans_path = os.path.join(fonts_dir, 'NotoSans-Regular.ttf')
            if os.path.exists(noto_sans_path):
                pdfmetrics.registerFont(TTFont('NotoSans', noto_sans_path))
                logging.info("Registered NotoSans font")
            
            # Register Noto Sans Devanagari (Hindi)
            noto_devanagari_path = os.path.join(fonts_dir, 'NotoSansDevanagari-Regular.ttf')
            if os.path.exists(noto_devanagari_path):
                pdfmetrics.registerFont(TTFont('NotoSansDevanagari', noto_devanagari_path))
                logging.info("Registered NotoSansDevanagari font")
            
            # Register Noto Serif Telugu (better quality)
            noto_serif_telugu_path = os.path.join(fonts_dir, 'NotoSerifTelugu-Regular.ttf')
            if os.path.exists(noto_serif_telugu_path):
                pdfmetrics.registerFont(TTFont('NotoSerifTelugu', noto_serif_telugu_path))
                logging.info("Registered NotoSerifTelugu font")
            
            # Register Noto Sans Telugu Bold
            noto_telugu_bold_path = os.path.join(fonts_dir, 'NotoSansTelugu-Bold.ttf')
            if os.path.exists(noto_telugu_bold_path):
                pdfmetrics.registerFont(TTFont('NotoSansTeluguBold', noto_telugu_bold_path))
                logging.info("Registered NotoSansTeluguBold font")
            
            # Fallback: Register regular Telugu font if available
            noto_telugu_path = os.path.join(fonts_dir, 'NotoSansTelugu-Regular.ttf')
            if os.path.exists(noto_telugu_path):
                pdfmetrics.registerFont(TTFont('NotoSansTelugu', noto_telugu_path))
                logging.info("Registered NotoSansTelugu font")
                
        except Exception as e:
            logging.warning(f"Could not register fonts: {e}")
    
    def get_font_for_language(self, language_code):
        """Get appropriate font for the target language"""
        font_mapping = {
            'hi': 'NotoSansDevanagari',  # Hindi
            'te': 'NotoSerifTelugu',     # Telugu (using better serif font)
            'ar': 'NotoSans',            # Arabic (fallback to NotoSans)
            'zh': 'NotoSans',            # Chinese (fallback to NotoSans)
            'ja': 'NotoSans',            # Japanese (fallback to NotoSans)
            'ko': 'NotoSans',            # Korean (fallback to NotoSans)
            'ru': 'NotoSans',            # Russian (fallback to NotoSans)
        }
        
        # Get the font name, defaulting to Helvetica if not found
        font_name = font_mapping.get(language_code, 'Helvetica')
        
        # Check if the font is actually registered, fallback to Helvetica if not
        try:
            registered_fonts = pdfmetrics.getRegisteredFontNames()
            if font_name not in registered_fonts:
                logging.warning(f"Font {font_name} not registered, using Helvetica")
                font_name = 'Helvetica'
        except:
            font_name = 'Helvetica'
            
        return font_name
        
    def extract_text(self, pdf_path):
        """Extract text from PDF using PyMuPDF"""
        try:
            doc = fitz.open(pdf_path)
            text_content = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                text_content += text + "\n\n"
            
            doc.close()
            return text_content.strip()
            
        except Exception as e:
            logging.error(f"Error extracting text from PDF: {str(e)}")
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def translate_text(self, text, source_lang, target_lang):
        """Fast translation using Google Translate with optimized processing"""
        try:
            # Clean and optimize text before translation
            cleaned_text = self._clean_text_for_translation(text)
            
            # For shorter texts, translate in one go
            if len(cleaned_text) <= 4500:
                logging.info(f"Translating text in single request ({len(cleaned_text)} chars)")
                result = self.translator.translate(
                    cleaned_text,
                    src=source_lang,
                    dest=target_lang
                )
                return result.text
            
            # For longer texts, use optimized chunking
            chunks = self._smart_split_text(cleaned_text, 4500)
            translated_chunks = []
            
            logging.info(f"Fast translation: {len(chunks)} chunks from {source_lang} to {target_lang}")
            
            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    start_time = time.time()
                    try:
                        result = self.translator.translate(
                            chunk,
                            src=source_lang,
                            dest=target_lang
                        )
                        translated_chunks.append(result.text)
                        
                        # Log timing for performance monitoring
                        elapsed = time.time() - start_time
                        logging.debug(f"Chunk {i+1}/{len(chunks)} translated in {elapsed:.2f}s")
                        
                    except Exception as chunk_error:
                        logging.warning(f"Chunk {i+1} failed: {chunk_error}")
                        # Fallback: try again with smaller chunk
                        if len(chunk) > 2000:
                            smaller_chunks = self._smart_split_text(chunk, 2000)
                            for small_chunk in smaller_chunks:
                                if small_chunk.strip():
                                    small_result = self.translator.translate(
                                        small_chunk,
                                        src=source_lang,
                                        dest=target_lang
                                    )
                                    translated_chunks.append(small_result.text)
                        else:
                            # If still fails, skip this chunk
                            logging.error(f"Skipping problematic chunk: {chunk[:100]}...")
                            translated_chunks.append(f"[Translation error for this section]")
                else:
                    translated_chunks.append("")
            
            return "\n\n".join(translated_chunks)
            
        except Exception as e:
            logging.error(f"Translation failed: {str(e)}")
            raise Exception(f"Translation service error: {str(e)}")
    
    def _clean_text_for_translation(self, text):
        """Clean text to improve translation speed and accuracy"""
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Remove page numbers and common PDF artifacts
        text = re.sub(r'\b\d+\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^Page \d+.*$', '', text, flags=re.MULTILINE)
        
        return text.strip()
    
    def _smart_split_text(self, text, max_size):
        """Improved text splitting that preserves sentence and paragraph boundaries"""
        if len(text) <= max_size:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        # First try to split by paragraphs
        paragraphs = text.split('\n\n')
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) + 2 <= max_size:
                if current_chunk:
                    current_chunk += '\n\n' + paragraph
                else:
                    current_chunk = paragraph
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                
                # If paragraph is too long, split by sentences
                if len(paragraph) > max_size:
                    sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                    current_chunk = ""
                    
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) + 1 <= max_size:
                            if current_chunk:
                                current_chunk += ' ' + sentence
                            else:
                                current_chunk = sentence
                        else:
                            if current_chunk:
                                chunks.append(current_chunk)
                            current_chunk = sentence
                else:
                    current_chunk = paragraph
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _split_text(self, text, max_size):
        """Split text into chunks while preserving paragraph structure"""
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # If adding this paragraph would exceed the limit
            if len(current_chunk) + len(paragraph) + 2 > max_size:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = paragraph
                else:
                    # If single paragraph is too long, split by sentences
                    sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) + 1 > max_size:
                            if current_chunk:
                                chunks.append(current_chunk)
                                current_chunk = sentence
                            else:
                                chunks.append(sentence)
                        else:
                            current_chunk += " " + sentence if current_chunk else sentence
            else:
                current_chunk += "\n\n" + paragraph if current_chunk else paragraph
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def create_pdf(self, text, output_path, original_filename, target_language='en'):
        """Create a new PDF with translated text using ReportLab"""
        try:
            # Create document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Get styles
            styles = getSampleStyleSheet()
            
            # Determine appropriate font for target language
            font_name = self.get_font_for_language(target_language)
            
            # Create custom styles with Unicode font support
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=16,
                spaceAfter=20,
                textColor='#2c3e50',
                fontName=font_name
            )
            
            # Enhanced Telugu styling for better readability
            if target_language == 'te':
                body_style = ParagraphStyle(
                    'TeluguBody',
                    parent=styles['Normal'],
                    fontSize=13,  # Larger font for Telugu
                    spaceAfter=16,
                    leading=20,   # More line spacing
                    textColor='#2c3e50',
                    fontName=font_name,
                    leftIndent=10,
                    rightIndent=10,
                    alignment=0  # Left align for better Telugu readability
                )
            else:
                body_style = ParagraphStyle(
                    'CustomBody',
                    parent=styles['Normal'],
                    fontSize=11,
                    spaceAfter=12,
                    leading=14,
                    textColor='#34495e',
                    fontName=font_name
                )
            
            # Build content
            story = []
            
            # Add title
            title = f"Translated Document: {original_filename}"
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 20))
            
            # Split text into paragraphs and add to story
            paragraphs = text.split('\n\n')
            
            for para_text in paragraphs:
                if para_text.strip():
                    # Clean up text for ReportLab
                    clean_text = self._clean_text_for_pdf(para_text.strip())
                    story.append(Paragraph(clean_text, body_style))
                    story.append(Spacer(1, 6))
            
            # Build PDF
            doc.build(story)
            
        except Exception as e:
            logging.error(f"Error creating PDF: {str(e)}")
            raise Exception(f"Failed to create translated PDF: {str(e)}")
    
    def _clean_text_for_pdf(self, text):
        """Clean text for ReportLab PDF generation with Telugu formatting"""
        # Escape special characters for ReportLab
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        
        # Enhanced formatting for Telugu poetry and elegant text
        if self._is_telugu_text(text):
            # Preserve poetic line breaks in Telugu
            lines = text.split('\n')
            formatted_lines = []
            
            for line in lines:
                line = line.strip()
                if line:
                    # Add elegant spacing for Telugu poetry
                    if self._is_poetic_line(line):
                        formatted_lines.append(f"<i>{line}</i>")
                    else:
                        formatted_lines.append(line)
            
            text = '<br/>'.join(formatted_lines)
        else:
            # Replace line breaks with proper paragraph breaks for other languages
            text = text.replace('\n', '<br/>')
        
        return text
    
    def _is_telugu_text(self, text):
        """Check if text contains Telugu characters"""
        telugu_range = range(0x0C00, 0x0C7F)
        return any(ord(char) in telugu_range for char in text)
    
    def _is_poetic_line(self, line):
        """Check if a Telugu line appears to be poetic"""
        poetic_words = [
            'చైతన్య', 'ఆశలు', 'భావనలు', 'కలలకే', 'విజయం', 'మనసు',
            'ఆకాశాన్ని', 'మార్గమై', 'కృషి', 'గెలిచిన', 'పుట్టిన', 'నూతన',
            'మధుర', 'తాకే', 'పల్లకిగా', 'ఆరోహణ', 'సాగిపోవాలి', 'మొదలవుతుంది'
        ]
        return any(word in line for word in poetic_words)
