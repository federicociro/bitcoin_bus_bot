# Bitcoin GroupHug Telegram Bot

## Overview
The Bitcoin GroupHug Telegram Bot is designed to facilitate Bitcoin transactions by receiving raw transaction data via Telegram and forwarding it to the GroupHug server. This bot serves as an intermediary, allowing users to easily submit their transactions through a friendly Telegram interface. It validates and batches transactions according to predefined rules before sending them to the backend server.

## Server Details
This bot interacts with the GroupHug server, which is located at [https://grouphug.bitcoinbarcelona.xyz/](https://grouphug.bitcoinbarcelona.xyz/). The server's source code is available on GitHub: [polespinasa/bitcoin-grouphug](https://github.com/polespinasa/bitcoin-grouphug.git).

## Features
- **Transaction Validation**: Ensures all transactions meet specific criteria (e.g., number of inputs and outputs, SigHash type) before forwarding.
- **TCP Communication**: Utilizes TCP to securely transmit transaction data to the GroupHug server.
- **User Interaction**: Provides interactive feedback to users about the status of their transactions, including validation errors and server responses.

## How It Works
1. **Receiving Transactions**: Users send their transaction data in raw format directly to the bot via Telegram.
2. **Validation**: The bot validates each transaction to ensure it conforms to necessary standards (like matching input and output counts, proper SigHash types, etc.).
3. **Sending to Server**: Valid transactions are sent to the GroupHug server using a TCP connection.
4. **Feedback**: The bot informs the user of the transaction status based on the server's response.

## Getting Started
To use this bot, follow these steps:
1. **Clone the Repository**: `git clone https://github.com/federicociro/bitcoin_bus_bot.git`
2. **Set Up Environment**:
    - Install dependencies: `pip install -r requirements.txt`
    - Edit `grouphug.py` file with necessary configurations (Telegram token, server IP, server port).
3. **Run the Bot**: `python bot.py`

## How to setup with CI/CD
To setup with CI/CD follow the [Deployment Documentation](DEPLOYMENT.md)

## Contribution
Contributions are welcome! If you'd like to improve the bot or suggest new features, please fork the repository and submit a pull request.

## License
This project is licensed under the GNU General Public License (GPL). See [LICENSE](LICENSE) for more information.

## Support
For support, join our Telegram group or open an issue in the GitHub repository.
