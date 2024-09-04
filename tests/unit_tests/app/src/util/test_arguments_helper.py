# @Disa
# class TestArgumentsHelper(TestCase):
#
#     def test_parse_arguments_with_defaults(self):
#         test_args = ["script_name"]
#         sys.argv = test_args
#
#         args = load_arguments()
#
#         self.assertEqual(args.quick_command_id, "")
#         self.assertEqual(args.client_id, "")
#         self.assertEqual(args.client_secret, "")
#         self.assertEqual(args.retry_count_callback, 10)
#         self.assertEqual(args.realm, DEFAULT_REALM)
#         self.assertEqual(args.base_branch, "")
#         self.assertEqual(args.compare_branch, "")
#         self.assertEqual(
#             args.directory, DEFAULT_DIRECTORY
#         )  # Change this to your DEFAULT_DIRECTORY
#         self.assertEqual(
#             args.extension, DEFAULT_EXTENSION
#         )  # Change this to your DEFAULT_EXTENSION
#         self.assertEqual(args.ignored_files, [])
#         self.assertEqual(args.ignored_directories, [])
#         self.assertEqual(
#             args.report_directory, DEFAULT_REPORT_DIRECTORY
#         )  # Change this to your DEFAULT_REPORT_DIRECTORY
#         self.assertEqual(
#             args.report_filename, DEFAULT_REPORT_FILENAME
#         )  # Change this to your DEFAULT_REPORT_FILENAME
#         self.assertEqual(args.retry_timeout, 10)
#         self.assertEqual(args.http_proxy, "")
#         self.assertEqual(args.https_proxy, "")
#
#     def test_parse_arguments_with_custom_values(self):
#         test_args = [
#             "script_name",
#             "--quick_command_id",
#             "test_command",
#             "--client_id",
#             "test_client_id",
#             "--client_secret",
#             "test_client_secret",
#             "--retry_count_callback",
#             "5",
#             "--realm",
#             "test_realm",
#             "--base_branch",
#             "main",
#             "--compare_branch",
#             "develop",
#             "--directory",
#             "test_directory",
#             "--extension",
#             "test_extension",
#             "--ignored_files",
#             "file1",
#             "file2",
#             "--ignored_directories",
#             "dir1",
#             "dir2",
#             "--report_directory",
#             "test_report_directory",
#             "--report_filename",
#             "test_report_filename",
#             "--retry_timeout",
#             "20",
#             "--http_proxy",
#             "http://proxy",
#             "--https_proxy",
#             "https://proxy",
#         ]
#         sys.argv = test_args
#
#         args = load_arguments()
#
#         self.assertEqual(args.quick_command_id, "test_command")
#         self.assertEqual(args.client_id, "test_client_id")
#         self.assertEqual(args.client_secret, "test_client_secret")
#         self.assertEqual(args.retry_count_callback, 5)
#         self.assertEqual(args.realm, "test_realm")
#         self.assertEqual(args.base_branch, "main")
#         self.assertEqual(args.compare_branch, "develop")
#         self.assertEqual(args.directory, "test_directory")
#         self.assertEqual(args.extension, "test_extension")
#         self.assertEqual(args.ignored_files, ["file1", "file2"])
#         self.assertEqual(args.ignored_directories, ["dir1", "dir2"])
#         self.assertEqual(args.report_directory, "test_report_directory")
#         self.assertEqual(args.report_filename, "test_report_filename")
#         self.assertEqual(args.retry_timeout, 20)
#         self.assertEqual(args.http_proxy, "http://proxy")
#         self.assertEqual(args.https_proxy, "https://proxy")
