import {
	ValidationOptions,
	ValidatorConstraint,
	ValidatorConstraintInterface,
	registerDecorator,
} from 'class-validator';
import { hash } from 'bcrypt';
import { DataRepository } from './data.repository';
import { Controller, Get } from '@nestjs/common';

@Controller('data')
@ValidatorConstraint({ async: true })
export class IsDataExistedConstraint implements ValidatorConstraintInterface {
	constructor(private readonly dataRepository: DataRepository) {}

	@Get(':hashValue')
	async validate(value: string) {
		return hash(value, 12).then((value) => {
			return this.dataRepository
				.findOneByHashValue(value)
				.then((data) => {
					return !data;
				});
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
