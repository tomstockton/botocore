#!/usr/bin/env python
# Copyright (c) 2012-2013 Mitch Garnaat http://garnaat.org/
# Copyright 2012-2013 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
import os
from tests import BaseEnvVar
import botocore.session


class TestS3Operations(BaseEnvVar):

    def setUp(self):
        super(TestS3Operations, self).setUp()
        self.environ['AWS_ACCESS_KEY_ID'] = 'foo'
        self.environ['AWS_SECRET_ACCESS_KEY'] = 'bar'
        self.session = botocore.session.get_session()
        self.s3 = self.session.get_service('s3')
        self.endpoint = self.s3.get_endpoint('us-east-1')
        self.bucket_name = 'foo'
        self.key_name = 'bar'

    def test_put_object(self):
        op = self.s3.get_operation('PutObject')
        file_path = os.path.join(os.path.dirname(__file__),
                                 'put_object_data')
        fp = open(file_path, 'rb')
        params = op.build_parameters(bucket=self.bucket_name,
                                     key=self.key_name,
                                     body=fp,
                                     acl='public-read',
                                     content_language='piglatin',
                                     content_type='text/plain')
        result = {'headers':
                  {'x-amz-acl': 'public-read',
                   'Content-Language': 'piglatin',
                   'Content-Type': 'text/plain'},
                  'payload': fp,
                  'uri_params': {'Bucket': 'foo', 'Key': 'bar'}}
        self.maxDiff = None
        self.assertEqual(params, result)

    def test_complete_multipart_upload(self):
        op = self.s3.get_operation('CompleteMultipartUpload')
        parts = {
            'parts': [
                {'e_tag': '123', 'part_number': 1},
                {'e_tag': '124', 'part_number': 2},
            ]
        }
        params = op.build_parameters(bucket=self.bucket_name,
                                     key=self.key_name,
                                     upload_id='upload_id',
                                     multipart_upload=parts)
        xml_payload = params['payload']
        # We should not see the <Parts><Part><...></Part></Parts>
        # element in the xml_payload.
        # Directly to Part, skipping Parts.
        self.assertIn('<CompleteMultipartUpload><Part>', xml_payload)
        self.assertIn('</Part></CompleteMultipartUpload>', xml_payload)
        # Explicitly check that <Parts> is not in the payload anywhere.
        self.assertNotIn('<Parts>', xml_payload)
        self.assertNotIn('</Parts>', xml_payload)


if __name__ == "__main__":
    unittest.main()
