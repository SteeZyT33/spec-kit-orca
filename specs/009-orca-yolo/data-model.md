# Data Model: Orca YOLO

## Entity: Yolo Run

- **Description**: One durable full-cycle Orca orchestration attempt.
- **Fields**:
  - run id
  - feature or artifact anchor
  - start mode
  - current stage
  - run policy
  - linked artifact paths
  - current outcome
  - stop reason
- **Relationships**:
  - references one or more upstream workflow artifacts
  - contains one current run policy
  - resolves to one current run outcome

## Entity: Run Stage

- **Description**: A defined workflow stage `orca-yolo` can enter, complete,
  pause at, or fail at.
- **Fields**:
  - stage id
  - stage order
  - required upstream artifacts
  - completion criteria
  - downstream handoff expectations
- **Relationships**:
  - belongs to the `Yolo Run` stage model
  - may emit or consume review, flow, and handoff artifacts

## Entity: Run Policy

- **Description**: The explicit settings controlling how a `Yolo Run` behaves.
- **Fields**:
  - ask level
  - start-from stage
  - resume mode
  - worktree mode
  - retry policy
  - PR completion policy
- **Relationships**:
  - belongs to one `Yolo Run`
  - governs one or more `Run Stage` transitions

## Entity: Run Outcome

- **Description**: The current or final status of a `Yolo Run`.
- **Fields**:
  - outcome state
  - timestamped status summary
  - blocking condition if any
  - final artifact links
- **Relationships**:
  - belongs to one `Yolo Run`
  - can reference review artifacts, PR outputs, and handoff state
