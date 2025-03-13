# Google Task List Desktop App

是不是覺得 Google Task List 網頁版不夠方便？這個專案提供了一個小型 [Google Task List](https://tasks.google.com/) 桌面應用程式。可以讓你更方便的在電腦桌面中新增、刪除、修改、查看任務清單。

<p align="center">
  <img src="./asset/Google_Tasks_2021.svg.png" width="100" alt="Google Tasks Logo">
</p>

## Usage

### 1.環境建立

因為 Google Task List API 需要使用 Google Cloud 專案的 OAuth 2.0 用戶端 ID，所以在使用前，請先建立 Google Cloud 專案，並啟用 Google Task List API。

> 參考：https://developers.google.com/tasks/quickstart/python?hl=zh-tw#set-up-environment

1. **啟用 API**

    使用 Google API 前，您必須先在 Google Cloud 專案中啟用這些 API。您可以在單一 Google Cloud 專案中啟用一或多個 API。
    - 在 Google Cloud 控制台中啟用 Google Tasks API。

2. **設定 OAuth 同意畫面**

    如果您要使用新的 Google Cloud 專案完成這個快速入門課程，請設定 OAuth 同意畫面。如果您已為 Cloud 專案完成這個步驟，請跳至下一節。

3. **授權電腦版應用程式的憑證**

    如要驗證使用者，並在應用程式中存取使用者資料，您需要建立一或多個 OAuth 2.0 用戶端 ID。用戶端 ID 可讓 Google 的 OAuth 伺服器識別單一應用程式。如果您的應用程式在多個平台上執行，則必須為每個平台建立專屬的用戶端 ID。

    - **將下載的 JSON 檔案儲存為 ./src/config/credentials.json。**

### 2.使用方式

1. 安裝依賴套件

    ```
    pip install -r requirements.txt
    ```

2. 執行程式

    ```
    python src/main.py
    ```

3. 開啟瀏覽器，並登入 Google 帳號，進行授權。

4. 授權完成後，盡情使用 Google Task List 桌面應用程式～

## References

- https://developers.google.com/tasks/quickstart/python