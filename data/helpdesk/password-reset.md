# EuroHealth Password Reset Procedure

Last reviewed: 2026-02-20
Owner: Identity and Access Management

## Supported reset methods

Employees can reset their password using one of these approved methods:
- self-service password reset portal
- servicedesk-assisted reset after identity verification

## Self-service reset

1. Open the Microsoft self-service password reset page.
2. Enter your EuroHealth email address.
3. Complete the MFA verification challenge.
4. Create a new password that meets the corporate complexity standard.
5. Wait up to 15 minutes for the new password to sync to VPN and legacy applications.

## Service desk-assisted reset

The service desk may guide the user through the process, but must not send passwords in chat or email.

Before performing an assisted reset, the agent or human analyst must remind the user that:
- identity verification is mandatory
- passwords are never shared in plain text
- privileged accounts require additional approval

## Known issues after reset

- VPN may still reject the new password for up to 15 minutes
- Outlook mobile may require the user to sign in again
- older cached Windows sessions may require device restart

## Escalate when

- the user has no access to MFA
- the user is locked out of both email and phone
- the account belongs to a privileged administrator
