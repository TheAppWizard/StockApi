from flask import Blueprint, render_template, request, jsonify
import pandas as pd
from datetime import datetime
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

stock_blueprint = Blueprint('stock_blueprint', __name__, template_folder='doc')

# Make sure the data directory exists
DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

FILE_PATH = os.path.join(DATA_DIR, 'data.xlsx')

COLUMNS = [
    'user_code', 'symbol', 'series', 'date', 'prev_close',
    'open_price', 'high_price', 'low_price', 'last_price', 'close_price',
    'avg_price', 'total_traded_qty', 'turnover', 'no_of_trades',
    'del_qty', 'del_to_trade_per'
]

def read_excel():
    """Read the Excel file with proper error handling"""
    try:
        if os.path.exists(FILE_PATH):
            logger.debug(f"Reading file from: {FILE_PATH}")
            # Read with openpyxl engine to ensure proper file closure
            df = pd.read_excel(FILE_PATH, engine='openpyxl')
            df['user_code'] = df['user_code'].astype(str)
            
            for col in COLUMNS:
                if col not in df.columns:
                    df[col] = None
            
            df = df[COLUMNS]
            logger.debug(f"Data read successfully. Shape: {df.shape}")
            return df
        else:
            logger.debug(f"File not found. Creating new DataFrame")
            return pd.DataFrame(columns=COLUMNS)
    except Exception as e:
        logger.error(f"Error reading Excel file: {str(e)}")
        return pd.DataFrame(columns=COLUMNS)

def write_excel(df):
    """Write to Excel file with proper error handling"""
    try:
        logger.debug("Writing to Excel file")
        # Use openpyxl engine and ensure proper file closure
        df.to_excel(FILE_PATH, index=False, engine='openpyxl')
        logger.debug("Write operation successful")
        return True
    except Exception as e:
        logger.error(f"Error writing to Excel file: {str(e)}")
        return False

@stock_blueprint.route('/stocks/<user_code>', methods=['GET'])
def get_stocks(user_code):
    try:
        logger.debug(f"Requested user_code: {user_code}")
        df = read_excel()
        user_code = str(user_code)
        df = df[df['user_code'] == user_code]
        
        if df.empty:
            return jsonify({
                "status": "error",
                "message": f"No records found for user_code: {user_code}",
                "data": []
            }), 404
        
        result = df.to_dict(orient='records')
        return jsonify({
            "status": "success",
            "count": len(result),
            "data": result
        })
    except Exception as e:
        logger.error(f"Error in get_stocks: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@stock_blueprint.route('/stock/<user_code>', methods=['POST'])
def create_stock(user_code):
    try:
        new_stock = request.json
        logger.debug(f"Received new stock data: {new_stock}")
        
        new_stock['user_code'] = str(user_code)
        
        missing_fields = [field for field in COLUMNS if field not in new_stock]
        if missing_fields:
            return jsonify({
                "status": "error",
                "message": f"Missing required fields: {missing_fields}"
            }), 400
        
        df = read_excel()
        
        if isinstance(new_stock.get('date'), str):
            new_stock['date'] = datetime.strptime(new_stock['date'], '%Y-%m-%d')
        
        new_df = pd.DataFrame([new_stock])
        df = pd.concat([df, new_df], ignore_index=True)
        
        if not write_excel(df):
            return jsonify({
                "status": "error",
                "message": "Failed to write to Excel file"
            }), 500
        
        return jsonify({
            "status": "success",
            "message": "Stock data created successfully",
            "data": new_stock
        }), 201
        
    except Exception as e:
        logger.error(f"Error in create_stock: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@stock_blueprint.route('/stock/<user_code>', methods=['PUT'])
def update_stock(user_code):
    try:
        update_data = request.json
        logger.debug(f"Attempting to update stocks for user_code: {user_code}")
        
        df = read_excel()
        user_code = str(user_code)
        
        if user_code not in df['user_code'].unique():
            return jsonify({
                "status": "error",
                "message": f"No records found for user_code: {user_code}"
            }), 404
        
        if isinstance(update_data.get('date'), str):
            update_data['date'] = datetime.strptime(update_data['date'], '%Y-%m-%d')
        
        mask = df['user_code'] == user_code
        for field, value in update_data.items():
            if field in COLUMNS and field != 'user_code':
                df.loc[mask, field] = value
        
        if not write_excel(df):
            return jsonify({
                "status": "error",
                "message": "Failed to write to Excel file"
            }), 500
        
        updated_records = df[mask].to_dict('records')
        
        return jsonify({
            "status": "success",
            "message": f"Successfully updated {len(updated_records)} records for user_code: {user_code}",
            "data": updated_records
        })
        
    except Exception as e:
        logger.error(f"Error in update_stock: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@stock_blueprint.route('/stock/<user_code>', methods=['DELETE'])
def delete_stock(user_code):
    try:
        logger.debug(f"Attempting to delete stocks for user_code: {user_code}")
        
        df = read_excel()
        user_code = str(user_code)
        
        if user_code not in df['user_code'].unique():
            return jsonify({
                "status": "error",
                "message": f"No records found for user_code: {user_code}"
            }), 404
        
        records_count = len(df[df['user_code'] == user_code])
        df = df[df['user_code'] != user_code]
        
        if not write_excel(df):
            return jsonify({
                "status": "error",
                "message": "Failed to write to Excel file"
            }), 500
        
        return jsonify({
            "status": "success",
            "message": f"Successfully deleted {records_count} records for user_code: {user_code}"
        })
        
    except Exception as e:
        logger.error(f"Error in delete_stock: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500