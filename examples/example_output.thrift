# Example Thrift IDL output from LINE APK extraction

# Type aliases for obfuscated names
typedef i32 C12999i2
typedef i32 C13013j2
typedef i32 W3
typedef i32 X3

# Enums
enum TalkErrorCode {
  E2EE_INVALID_PROTOCOL = 81,
  E2EE_RETRY_ENCRYPT = 82,
  E2EE_UPDATE_SENDER_KEY = 83,
  E2EE_UPDATE_RECEIVER_KEY = 84,
  E2EE_INVALID_ARGUMENT = 85,
  E2EE_INVALID_VERSION = 86,
  E2EE_SENDER_DISABLED = 87,
  E2EE_RECEIVER_DISABLED = 88,
  E2EE_SENDER_NOT_ALLOWED = 89,
  E2EE_RECEIVER_NOT_ALLOWED = 90,
  E2EE_RESEND_FAIL = 91,
  E2EE_RESEND_OK = 92,
  E2EE_UPDATE_PRIMARY_DEVICE = 94,
  E2EE_PRIMARY_NOT_SUPPORT = 97,
  E2EE_RETRY_PLAIN = 98,
  E2EE_RECREATE_GROUP_KEY = 99,
  E2EE_GROUP_TOO_MANY_MEMBERS = 100
}

# Structs
struct GetContactsV3Response {
  1: list<i32> responses
}

struct DeleteOtherFromChatResponse {
}

struct CancelChatInvitationResponse {
}

struct EstablishE2EESessionRequest {
  1: string clientPublicKey
}

struct EstablishE2EESessionResponse {
  1: string sessionId,
  2: string serverPublicKey,
  3: i64 expireAt
}

struct GetE2EEKeyBackupInfoResponse {
  1: string blobHeaderHash,
  2: string blobPayloadHash,
  3: set<i32> missingKeyIds,
  4: i64 createdTime
}

# Services
service GroupTalkService {
  CancelChatInvitationResponse cancelChatInvitation(1: C12999i2 request),
  DeleteOtherFromChatResponse deleteOtherFromChat(1: W3 request),
}

service E2eeKeyBackupService {
  void callWithResult(1: binary request)
}

service authService {
  String confirmE2EELogin(1: binary request),
  void continueLoginAfterPinVerification(1: binary request),
}
