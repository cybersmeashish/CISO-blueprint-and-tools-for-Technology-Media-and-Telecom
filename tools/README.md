# Catalog and migration checker

```sh
docker --context orbstack exec ciso-industry-3-dev python tools/check_catalog.py --output evidence
```

This standard-library tool verifies expected sector folders, document links and any migrated source hashes. It records actual checks; it is not a CISO control assessor.
