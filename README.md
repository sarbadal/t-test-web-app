# T-Test Analysis Web Application

A Flask-based web application for performing statistical t-tests with an intuitive interface. This application supports three types of t-tests: one-sample, paired, and two-sample t-tests.

## Features

- **Multiple T-Test Types**: Supports one-sample, paired, and two-sample t-tests
- **JSON Data Upload**: Easy data input via JSON file uploads
- **Configurable Confidence Levels**: Customizable confidence levels for statistical analysis
- **Session Management**: Secure login system with session management
- **Cloud Ready**: Deployable to Google Cloud Functions
- **Statistical Results**: Comprehensive output including t-statistics, p-values, and means

## Project Structure

```
t-test/
├── main.py                   # Application entry point
├── db_init.py                # Database management CLI
├── requirements.txt          # Python dependencies
├── deployment.sh             # Google Cloud deployment script
├── README.md                 # Project documentation
├── sample_data/              # Sample JSON data files
├── src/
│   ├── app/                  # Flask application package
│   │   ├── __init__.py
│   │   ├── env_vars.py       # Environment variables
│   │   ├── run.py            # Flask app factory
│   │   ├── routes/           # Application routes
│   │   ├── services/         # Business logic layer
│   │   ├── models/           # SQLAlchemy models
│   │   ├── utils/            # Utility modules
│   │   ├── templates/        # HTML templates
│   │   └── static/           # Static assets
│   ├── ml/                   # Statistics module
│   │   ├── __init__.py
│   │   └── ttest.py
│   └── instance/             # Flask instance folder (SQLite DB lives here by default)
└── tests/                    # Automated tests
```

## Installation

### Prerequisites

- Python 3.11+
- pip package manager

### Local Setup

1. Clone or download the project to your local machine

2. Navigate to the project directory:
   ```bash
   cd t-test
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (configure values in `src/app/env_vars.py`, or use environment variables)

5. Run the application:
   ```bash
   python main.py
   ```

The application will be available at `http://localhost:5000`

### Database and instance path

- The Flask `instance_path` is explicitly configured to `src/instance`.
- By default, SQLite is stored at `src/instance/ttest_analysis.db`.
- You can override this by setting the `DATABASE_URL` environment variable.

Example custom database URL:

```bash
export DATABASE_URL="sqlite:////absolute/path/to/custom.db"
```

### Database CLI commands

Use the built-in CLI for initialization, seeding, and user creation:

```bash
python db_init.py --help
python db_init.py init
python db_init.py seed
python db_init.py create-user
python db_init.py create-admin
```

## Usage

### Data Format

The application accepts JSON files with specific formats depending on the type of t-test:

#### One-Sample T-Test
```json
{
  "data": [23.5, 25.1, 22.8, 24.3, 26.7, 23.9, 25.5, 24.1]
}
```

#### Paired T-Test
```json
{
  "before": [120, 118, 125, 122, 119, 124, 121, 123],
  "after": [115, 112, 118, 116, 113, 117, 114, 116]
}
```

#### Two-Sample T-Test
```json
{
  "group1": [23.1, 24.5, 22.8, 25.2, 23.7, 24.9],
  "group2": [21.3, 22.1, 20.8, 22.7, 21.9, 22.4]
}
```

### API Endpoint

#### POST `/analyze`

Performs t-test analysis on uploaded data.

**Parameters:**
- `file`: JSON file containing the data
- `confidence`: Confidence level (default: 0.95)

**Authentication:** Requires active session (user must be logged in)

**Response:**
```json
{
  "test_type": "One-sample t-test",
  "sample_size": 20,
  "confidence_level": 0.95,
  "t_statistic": 15.23,
  "p_value": 0.0001,
  "mean": 24.5
}
```

### Statistical Tests

1. **One-Sample T-Test**: Tests if the sample mean differs significantly from zero
2. **Paired T-Test**: Compares two related samples (e.g., before/after measurements)
3. **Two-Sample T-Test**: Compares means of two independent groups

## Sample Data

The repository includes several sample data files for testing in `sample_data/`:

- `sample_data/test_data_one_sample.json`: One-sample t-test data
- `sample_data/test_data_paired.json`: Paired t-test data (small sample)
- `sample_data/test_data_paired_large.json`: Paired t-test data (large sample)
- `sample_data/test_data_two_sample.json`: Two-sample t-test data
- `sample_data/test_data_two_sample_large.json`: Two-sample t-test data (large sample)

## Cloud Deployment

### Google Cloud Functions

The application is configured for deployment to Google Cloud Functions using the provided deployment script.

1. Ensure you have the Google Cloud CLI installed and configured
2. Update the project ID in `deployment.sh` if necessary
3. Run the deployment script:
   ```bash
   ./deployment.sh
   ```

The function will be deployed as `t-test-analysis` in the `us-central1` region.

## Dependencies

- **Flask 3.0.0**: Web framework
- **pandas 2.1.4**: Data manipulation and analysis
- **scipy 1.13.1**: Statistical functions
- **functions-framework 3.5.0**: Google Cloud Functions framework

## Security Features

- Session-based authentication
- Secure session management with configurable timeout
- Protected analysis endpoints requiring authentication

## Development

### Local Development

For local development, the application runs in debug mode with the following configuration:
- Host: `0.0.0.0`
- Port: `5000`
- Debug: `True`

### Testing

Use the provided sample JSON files to test different types of t-tests:

1. Upload a sample data file through the web interface
2. Select appropriate confidence level
3. Submit for analysis
4. Review the statistical results

## License

This project is available for educational and research purposes.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues or questions regarding the t-test analysis application, please review the code documentation and sample data formats provided.