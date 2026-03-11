# Feature Specification: Savings Circles Creation

**Feature Branch**: `001-savings-circles`
**Created**: 2026-03-11
**Status**: Draft
**Input**: User description: "savings circles creation"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create a Savings Circle (Priority: P1)

An authenticated user creates a new savings circle by providing the group name, contribution amount per cycle, number of members, payment frequency, start date, number of payouts (which determines the end date), and optional penalty/grace period rules.

**Why this priority**: This is the core feature — without circle creation, nothing else exists. It is the entry point for the entire savings circle product.

**Independent Test**: Can be fully tested by submitting a valid circle creation request and verifying the circle is persisted and returned with a unique ID and computed end date.

**Acceptance Scenarios**:

1. **Given** an authenticated user with a valid access token, **When** they submit a circle creation request with all required fields, **Then** a new circle is created and the response includes the circle's unique ID, computed end date, and a 201 status.
2. **Given** an authenticated user, **When** they submit a request missing any required field (e.g., no name, no amount), **Then** the system returns a 422 error listing the missing fields.
3. **Given** an authenticated user, **When** they submit an amount of 0 or negative, **Then** the system returns a 422 validation error.
4. **Given** an authenticated user, **When** they submit a `payout_count` of 0 or negative, **Then** the system returns a 422 validation error.
5. **Given** an unauthenticated request (no or invalid token), **When** they attempt to create a circle, **Then** the system returns 401 Unauthorized.

---

### User Story 2 - View Savings Circles (Priority: P2)

An authenticated user retrieves the list of savings circles they have created.

**Why this priority**: Users need to see their circles immediately after creation to confirm the action was successful and to navigate to the savings view.

**Independent Test**: Can be fully tested by creating a circle and then fetching the circles list, verifying the new circle appears.

**Acceptance Scenarios**:

1. **Given** an authenticated user who has created at least one circle, **When** they request their circles list, **Then** the response includes all circles belonging to them with key details (name, amount, frequency, start date, end date, status).
2. **Given** an authenticated user with no circles, **When** they request their circles list, **Then** the response returns an empty list with a 200 status.

---

### User Story 3 - End Date Auto-Computation (Priority: P1)

The system automatically computes and stores the end date based on start date, payout count, and frequency — the user never manually selects an end date.

**Why this priority**: Ensures data integrity and removes a common source of user error. The mobile app relies on this computation being server-side authoritative.

**Independent Test**: Can be fully tested by creating a circle with a known start date, payout count, and frequency, then asserting the returned end date matches the expected computed value.

**Acceptance Scenarios**:

1. **Given** a start date of 2026-04-01, payout count of 4, and frequency "monthly", **When** a circle is created, **Then** the end date stored and returned is 2026-08-01.
2. **Given** a start date of 2026-04-01, payout count of 4, and frequency "weekly", **When** a circle is created, **Then** the end date is 2026-04-29 (4 × 7 days).
3. **Given** a start date of 2026-04-01, payout count of 2, and frequency "quarterly", **When** a circle is created, **Then** the end date is 2026-10-01 (2 × 3 months).

---

### Edge Cases

- What happens when `start_date` is in the past? Reject with 422 — start date must be today or a future date.
- What happens when `members` is 0 or 1? Reject — minimum 2 members required for a group savings circle.
- What happens when `penalty_percent` exceeds 100? Reject with 422.
- What happens when frequency is an unrecognised value? Reject with 422 — must be one of: daily, weekly, bi-weekly, monthly, quarterly.
- What happens when two circles have the same name for the same user? Allow — names are not unique per user.
- What happens when `payout_count` is very large (e.g., 1000 monthly payouts)? Accept — no upper limit beyond positive integer validation.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow an authenticated user to create a savings circle with: name, amount (naira), members count, frequency, start date, payout count, penalty percent, grace period days, and start-when-members flag.
- **FR-002**: System MUST compute the circle's end date server-side as: start date + (payout count × frequency interval). The client does not supply an end date.
- **FR-003**: System MUST validate that start date is today or a future date — past dates are rejected.
- **FR-004**: System MUST validate frequency is one of: daily, weekly, bi-weekly, monthly, quarterly.
- **FR-005**: System MUST validate amount is a positive number greater than zero.
- **FR-006**: System MUST validate payout_count is a positive integer greater than zero.
- **FR-007**: System MUST validate members is at least 2.
- **FR-008**: System MUST validate penalty_percent is between 0 and 100 inclusive.
- **FR-009**: System MUST associate the circle with the authenticated user as its creator/owner.
- **FR-010**: System MUST return the created circle's unique ID and computed end date in the creation response.
- **FR-011**: System MUST allow the authenticated user to retrieve their list of savings circles.
- **FR-012**: System MUST reject unauthenticated requests with 401 Unauthorized.

### Key Entities

- **SavingsCircle**: A group savings arrangement. Attributes: unique ID, creator user ID, name, contribution amount (naira), member count, frequency (daily/weekly/bi-weekly/monthly/quarterly), start date, end date (server-computed), payout count, penalty percent (0–100), grace period days, start-when-members flag (boolean), status (pending/active/completed), created-at timestamp.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can submit a circle creation request and receive a confirmed response (with ID and end date) in under 2 seconds under normal load.
- **SC-002**: 100% of created circles have a correctly computed end date matching start date + (payout count × frequency interval).
- **SC-003**: All invalid inputs (missing fields, out-of-range values, unrecognised frequency, past start date) are rejected with a descriptive error before any data is persisted.
- **SC-004**: An authenticated user can retrieve their full circles list in a single request without pagination required for typical usage (under 50 circles).
- **SC-005**: Zero circles are created without a valid authenticated identity — all unauthenticated creation attempts are rejected.

## Assumptions

- `amount` is the per-cycle contribution per member in Nigerian Naira (₦), stored as a decimal value.
- `start_when_members` is a boolean: when true, the circle only activates when the required member count has joined; when false, it starts on the scheduled start date regardless of join count.
- `grace_period_days` defaults to 0 if not provided.
- `penalty_percent` defaults to 0 if not provided.
- The circles list endpoint returns only circles where the requesting user is the creator; member-joining flow is out of scope for this feature.
- Payout order (which member gets paid in which cycle) is out of scope — that is a separate scheduling feature.
