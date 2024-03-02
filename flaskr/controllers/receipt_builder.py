from reportlab.platypus import Paragraph, TableStyle 
from reportlab.lib import colors 
from reportlab.lib.styles import getSampleStyleSheet


def build_receipt_template() -> tuple[Paragraph, TableStyle]:
    # Standard stylesheet defined within reportlab itself. 
    styles = getSampleStyleSheet() 

    title_style = styles['Heading1'] 
    
    ''' 
    Template reference

    DATA = [ 
        [ "Date" , "Product", "Price (USD)" ], 
        [ "16/11/2020", "", "10,999.00/-"], 
        [ "16/11/2020", "", "9,999.00/-"],
        [ "Sub Total", "", "20,9998.00/-"],
        [ "Discount", "", "-3,000.00/-"],
        [ "Total", "", "17,998.00/-"],
    ] 

    '''

    # 0: left, 
    # 1: center, 
    # 2: right 
    title_style.alignment = 1
    
    title = Paragraph('Payment receipt - Viki', title_style ) 
    
    style = TableStyle( 
        [ 
            ( 'BOX', (0, 0 ), (-1, -1 ), 1, colors.black ), 
            ( 'GRID', (0, 0 ), (4, 4 ), 1, colors.black ), 
            ( 'BACKGROUND', (0, 0 ), (3, 0), colors.gray ), 
            ( 'TEXTCOLOR', (0, 0 ), (-1, 0), colors.black ), 
            ( 'ALIGN', (0, 0 ), (-1, -1 ), 'CENTER'), 
            ( 'BACKGROUND', (0, 1 ), (-1, -1 ), colors.white ), 
        ] 
    ) 
    
    return title, style