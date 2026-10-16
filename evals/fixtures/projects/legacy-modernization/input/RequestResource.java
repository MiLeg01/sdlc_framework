package example.request;

final class RequestResource {
    private final RequestService service;

    RequestResource(RequestService service) {
        this.service = service;
    }

    String submit(String requestId, String requestType) {
        if (requestId == null || requestId.isBlank()) {
            throw new IllegalArgumentException("requestId");
        }
        return service.submit(requestId, requestType);
    }
}

interface RequestService {
    String submit(String requestId, String requestType);
}
