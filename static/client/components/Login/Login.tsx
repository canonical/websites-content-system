import { useCallback } from "react";

import { Button, LoginPageLayout } from "@canonical/react-components";

// import { AuthServices } from "@/services/api/services/auth";

const Login = (): JSX.Element => {
  const handleLogin = useCallback(() => {
    // AuthServices.login("/").then((response) => {
    //   console.log({ response });
    // });
    window.open("http://0.0.0.0:8104/login?next=/");
  }, []);

  return (
    <LoginPageLayout title="Login with Ubuntu SSO">
      <Button appearance="positive" onClick={handleLogin}>
        Login
      </Button>
    </LoginPageLayout>
  );
};

export default Login;
