# EuroHealth VPN Access Guide

Last reviewed: 2026-02-14
Owner: IT Workplace Services
Applies to: employees and long-term contractors with approved remote-access rights

## When to use VPN

Use the EuroHealth VPN when you are outside the office network and need access to:
- internal claims platforms
- on-prem file shares
- internal Confluence spaces marked "corporate only"
- administrative tools that are not exposed through Microsoft 365

## Before you start

You need all of the following:
- an active EuroHealth user account
- MFA already enrolled in Microsoft Authenticator
- the approved VPN client installed from Software Center
- manager approval for remote access if you are a new starter or contractor

## First-time setup

1. Connect your device to the internet.
2. Open `Software Center` and install `EuroHealth Secure Connect`.
3. Launch the VPN client.
4. Enter the server name `vpn.eurohealth.example`.
5. Sign in with your EuroHealth email address.
6. Approve the MFA challenge in Microsoft Authenticator.
7. Wait for the status to change to `Connected`.

## Daily login steps

1. Open `EuroHealth Secure Connect`.
2. Select the `Standard Employee Access` profile.
3. Sign in with your EuroHealth email address and password.
4. Approve the MFA request.
5. Confirm the client shows `Connected` before opening internal systems.

## If login fails

- If MFA does not arrive, confirm your phone has internet access and try `Resend`.
- If the client shows `Access denied`, your remote-access role may be missing. Open a ServiceNow ticket for `Access / VPN`.
- If the password was recently changed, wait up to 15 minutes and try again.
- If the client says `Profile not found`, reinstall the client from Software Center.

## What the helpdesk should never do in chat

- never send passwords, temporary passwords, or shared secrets
- never bypass MFA
- never approve access without the formal access request

## Escalation path

If the issue remains unresolved after reinstalling the client and retrying MFA, route the case to:
- `L2 Network Support` for connectivity errors
- `Identity & Access Management` for role or entitlement issues
