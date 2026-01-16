/**
 * Extract user-friendly error message from axios or fetch errors
 * @param {Error} error - The error object
 * @returns {string} - User-friendly error message
 */
export function getErrorMessage(error) {
  // Axios error with response from backend
  if (error.response) {
    const status = error.response.status;
    const data = error.response.data;

    // Backend sent an error message
    if (typeof data === "string") {
      return `⚠️ Error (${status}): ${data}`;
    }

    if (data && data.detail) {
      return `⚠️ Error (${status}): ${data.detail}`;
    }

    // Standard HTTP status messages
    const statusMessages = {
      400: "Bad request. Please check your input.",
      401: "Unauthorized. Please login again.",
      403: "Access denied.",
      404: "Not found. Bot or session may no longer exist.",
      422: "Invalid input. Please check your message.",
      429: "Too many requests. Please try again later.",
      500: "Server error. Please try again.",
      503: "Service unavailable. Please try again later.",
    };

    return `⚠️ ${statusMessages[status] || `Error ${status}`}`;
  }

  // Axios error without response (network error, timeout, etc.)
  if (error.code) {
    const codeMessages = {
      ECONNABORTED: "Request timeout. Please check your connection.",
      ECONNREFUSED: "Cannot connect to server. Is it running?",
      ENOTFOUND: "Server not found. Check the API URL.",
      ERR_NETWORK: "Network error. Please check your connection.",
    };

    return `⚠️ ${codeMessages[error.code] || `Connection error: ${error.message}`}`;
  }

  // Regular JavaScript error
  if (error instanceof Error) {
    return `⚠️ ${error.message}`;
  }

  // Fallback
  return "⚠️ An unexpected error occurred. Please try again.";
}

/**
 * Extract session-related errors (for debugging)
 * @param {Error} error - The error object
 * @returns {boolean} - True if it's a session-related error
 */
export function isSessionError(error) {
  if (error.response?.status === 404) {
    const detail = error.response.data?.detail || "";
    return detail.includes("Conversation") || detail.includes("Session");
  }
  return false;
}
