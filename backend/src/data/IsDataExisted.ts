import {
	ValidationOptions,
	ValidatorConstraint,
	ValidatorConstraintInterface,
	registerDecorator,
} from 'class-validator';
import { Md5 } from 'ts-md5';
import { Controller, Get } from '@nestjs/common';
import { DataService } from './data.service';

@Controller('data')
@ValidatorConstraint({ async: true })
export class IsDataExistedConstraint implements ValidatorConstraintInterface {
	constructor(private dataRepository: DataService = new DataService()) {}

	@Get(':hashValue')
	validate(value: string) {
		return this.dataRepository
			.findOneBy({ hashValue: Md5.hashStr(value) })
			.then((data) => {
				return !data;
			});
	}
}

export function IsDataExisted(validationOptions?: ValidationOptions) {
	return function (object: any, propertyName: string) {
		registerDecorator({
			target: object.constructor,
			propertyName: propertyName,
			options: validationOptions,
			constraints: [],
			validator: IsDataExistedConstraint,
		});
	};
}
