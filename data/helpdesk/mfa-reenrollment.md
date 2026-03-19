# EuroHealth MFA Re-enrollment

Last reviewed: 2026-02-25
Owner: Identity and Access Management

## When re-enrollment is needed

MFA re-enrollment is required when:
- the user changed or lost their phone
- Microsoft Authenticator was removed
- the user cannot receive push notifications or codes after device replacement

## Safe support steps

1. Confirm the user is requesting help for their own account.
2. Instruct the user to contact the service desk through the approved channel if identity verification is needed.
3. After verification, remove the old MFA registration in the identity portal.
4. Ask the user to sign in again and register Microsoft Authenticator on the new device.
5. Test one push notification and one backup code method if available.

## Security rules

- never ask the user to share MFA codes in chat
- never approve sign-in prompts on behalf of the user
- never store recovery codes in tickets

## Escalate when

- the user cannot complete identity verification
- the account is privileged
- repeated fraud alerts appear during sign-in
