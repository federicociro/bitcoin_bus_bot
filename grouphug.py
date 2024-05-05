from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

import bitcoin
import asyncio
import socket

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Send me a Bitcoin transaction in raw format.')

async def handle_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tx_raw = update.message.text
    if validate_transaction(tx_raw):
        message = f"add_tx {tx_raw}"
        response = await send_to_server(message)
        if response:
            await update.message.reply_text('Transaction formatted and sent for processing. Server responded with: ' + response)
        else:
            await update.message.reply_text('Failed to communicate with server.')
    else:
        await update.message.reply_text('Transaction does not meet the required criteria.')

async def send_to_server(message):
    host = 'INSERT_SERVER_IP'
    port = 3000
    reader, writer = None, None
    try:
        reader, writer = await asyncio.open_connection(host, port)
        writer.write(message.encode())
        await writer.drain()
        response = await reader.read(100)
        print(f"Server response: {response.decode()}")
        return response.decode()
    except Exception as e:
        print(f"Failed to send to server: {e}")
        return None
    finally:
        if writer:
            writer.close()
            await writer.wait_closed()

def validate_transaction(tx_raw):
    try:
        tx = bitcoin.deserialize(tx_raw)
        # Check for equal number of inputs and outputs
        if len(tx['ins']) != len(tx['outs']):
            return False
        # Check for maximum 5 inputs
        if len(tx['ins']) > 5:
            return False
        # Check locktime
        if tx['locktime'] != 0:
            return False
        # Check each input for the correct SigHash type
        for input in tx['ins']:
            if 'witness' in input:
                witness = input['witness']
                if not witness:
                    return False
                # Assuming the SigHash type is the last byte of the last item in the witness
                last_byte = witness[-1][-1]
                if last_byte != (0x83):  # Hex 0x83 stands for SigHashType.SINGLE | SigHashType.ANYONECANPAY
                    return False
            else:
                return False
        return True
    except Exception as e:
        print(f"Error during transaction validation: {e}")
        return False

def main() -> None:
    application = Application.builder().token('INSERT_BOT_TOKEN').build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_transaction))

    application.run_polling()

if __name__ == '__main__':
    main()
