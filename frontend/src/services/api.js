import axios from "axios";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
  timeout: 180000,
});

export async function analyzeAssignment(file, customReference = "") {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("custom_reference", customReference);

  const { data } = await apiClient.post("/analyze", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return data;
}
