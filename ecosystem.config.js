module.exports = {
  apps: [
    {
      name: "convenience-store-app",
      script: "app.py",
      interpreter: "python3",
      env: {
        FLASK_ENV: "production",
        FLASK_APP: "app.py"
      }
    }
  ]
}