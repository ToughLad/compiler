public class UserServiceClient {
    public final void getUserInfo(String userId) throws Exception {
        b("getUserInfo", userId);
    }
    static class getUserInfo_args {
        public String userId;
    }
    static class getUserInfo_result {
        public UserResponse success;
        public UserException ex;
    }
}