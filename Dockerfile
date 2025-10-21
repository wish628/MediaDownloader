FROM kivy/buildozer:latest

WORKDIR /app

# Copy all files
COPY . .

# Install project dependencies
RUN pip install -r requirements.txt

# Build the APK
RUN buildozer android debug

CMD ["bash"]