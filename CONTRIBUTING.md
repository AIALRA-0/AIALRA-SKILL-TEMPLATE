# Contributing

Changes to the universal template affect every future Skill repository. Keep them backward-compatible where possible and test them in a freshly generated repository.

Required evidence:

1. The runtime invariant being added or changed.
2. A regression test for success and the nearest failure mode.
3. Confirmation that generated draft repositories remain non-executable.
4. Confirmation that stable core mutation is detected.
5. Confirmation that learning changes cannot modify core or lose archived events.
6. SemVer impact and changelog entry.

Run all repository checks before committing. Do not place generated repositories inside this template repository.
