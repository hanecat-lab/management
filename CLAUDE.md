# management

## 作業方針

- 小規模修正ではサブエージェントを使用しない
- リポジトリ全体分析は依頼時のみ実施
- レビューは依頼時のみ実施
- 修正後は最小限の確認のみ行う

## データの取り扱い

- 個人の実データ(家計簿・評価などのエクスポートJSON/CSV)はこのリポジトリにコミットしない
- バックアップは非公開リポジトリ care-data-backup に置く
- レシピ等のアプリ用コンテンツデータ(additional-recipes.json など)はコミットしてよい

## バージョン管理

- kakeibo.html の `APP_VERSION`・ver.txt、hyoka.html の `HYOKA_VERSION`・hyoka-ver.txt は
  GitHub Actions(auto-version.yml)が自動更新するため手動で変更しない
- 新規アプリは app-template.html を雛形にし、自動更新を使う場合は auto-version.yml に対象を追記する
